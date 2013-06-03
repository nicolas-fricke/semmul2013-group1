#!/usr/bin/python
# -*- coding: utf-8 -*-

######################################################################################
# Preprocesses the tags from the metadata crawling
#
# config file: ../config.cfg
#
# Use config.cfg.template as template for this file
#
#
# authors: tino junge, mandy roick
# mail: tino.junge@student.hpi.uni-potsdam.de, mandy.roick@student.hpi.uni-potsdam.de
######################################################################################

import numpy as np
from scipy import linalg
import os
import operator
from collections import defaultdict
# Import own modules
import sys
sys.path.append('../helpers')
from general_helpers import *
from tag_preprocessing import *

output_file_name = ""
error_occuring = 0


################     Laplace Matrix       ###################################
def calculate_negative_adjacency_matrix(tag_index_dict, tag_co_occurrence_histogram):
  negative_adjacency_matrix = np.zeros((len(tag_index_dict),len(tag_index_dict)))
  for (tag1, tag2) in tag_co_occurrence_histogram:
    negative_adjacency_matrix[tag_index_dict[tag1]][tag_index_dict[tag2]] = -1
    negative_adjacency_matrix[tag_index_dict[tag2]][tag_index_dict[tag1]] = -1
  return negative_adjacency_matrix

# set diagonal of laplace to degrees of vertices
def add_diagonal_matrix_to_adjacency(matrix):
  for i,line in enumerate(matrix):
    matrix[i][i] = sum(line)*(-1)
  return matrix

def calculate_laplace_matrix(tag_index_dict, tag_co_occurrence_histogram):
  laplace_matrix = calculate_negative_adjacency_matrix(tag_index_dict, tag_co_occurrence_histogram)
  print "Done calculation of adjacency matrix"
  laplace_matrix = add_diagonal_matrix_to_adjacency(laplace_matrix)
  print "Done calculation of diagonal matrix"
  return laplace_matrix

################     Spectral Bisection       ###################################
def calculate_second_highest_eigen_vector(eigen_values, eigen_vectors):
  index_of_highest_eigen_value = 0
  index_of_second_highest_eigen_value = 0
  for index, eigen_value in enumerate(eigen_values):
    if(eigen_value > eigen_values[index_of_second_highest_eigen_value]):
      if(eigen_value > eigen_values[index_of_highest_eigen_value]):
        index_of_second_highest_eigen_value = index_of_highest_eigen_value
        index_of_highest_eigen_value = index
      else:
        index_of_second_highest_eigen_value = index

  return eigen_vectors[index_of_second_highest_eigen_value]

def calculate_second_smallest_eigen_vector(eigen_values, eigen_vectors):
  index_of_smallest_eigen_value = -1
  index_of_second_smallest_eigen_value = -1
  for index, eigen_value in enumerate(eigen_values):
    if eigen_value == 0:
      if index_of_smallest_eigen_value == -1:
        index_of_smallest_eigen_value = index
      else:
        index_of_second_smallest_eigen_value = index
        break
    elif eigen_value > 0:
      if (index_of_second_smallest_eigen_value == -1) or (eigen_value < eigen_values[index_of_second_smallest_eigen_value]):
        index_of_second_smallest_eigen_value = index
  return eigen_vectors[index_of_second_smallest_eigen_value]

def create_clusters(separation_vector, index_tag_dict):
  tag_cluster1 = []
  tag_cluster2 = []

  # '>=' instead of '>' results in overlapping clusters
  for index, vector_value in enumerate(separation_vector):
    if vector_value > 0:
      tag_cluster1.append(index_tag_dict[index])
    if vector_value < 0:
      tag_cluster2.append(index_tag_dict[index])

  return tag_cluster1, tag_cluster2

def spectral_bisection(matrix, index_tag_dict):
  eigen_values, eigen_vectors = linalg.eig(matrix)
  print "Done calculate eigenvalues"
  partitioning_vector = calculate_second_smallest_eigen_vector(eigen_values, eigen_vectors)
  print "Done find vector for second highest eigenvalue"
  return create_clusters(partitioning_vector, index_tag_dict)

################     Spectral Bisection       ###################################

def calculate_parent_weight(tag_co_occurrence_histogram):
  return 2*sum(tag_co_occurrence_histogram.values())

def calculate_child_weights(tag_co_occurrence_histogram, cluster1, cluster2):
  child1_weight = 0
  child2_weight = 0
  for (tag1, tag2), weight in tag_co_occurrence_histogram.items():
    if tag1 in cluster1 and tag2 in cluster1:
      child1_weight += weight
    if tag1 in cluster2 and tag2 in cluster2:
      child2_weight += weight

  # weights need to be doubled because we have to regard the opposite direction of every edge
  child1_weight *= 2
  child2_weight *= 2
  return child1_weight, child2_weight

def calculate_inter_cluster_weights(tag_co_occurrence_histogram, cluster1, cluster2):
  inter_cluster_child1_parent_weight = 0
  inter_cluster_child2_parent_weight = 0
  for (tag1, tag2), weight in tag_co_occurrence_histogram.items():
    if tag1 in cluster1 and tag2 in cluster2:
      inter_cluster_child1_parent_weight += weight
    if tag1 in cluster2 and tag2 in cluster1:
      inter_cluster_child2_parent_weight += weight
  return inter_cluster_child1_parent_weight, inter_cluster_child2_parent_weight

def calculate_modularity_of_child_cluster(child_weight, inter_cluster_weight, parent_weight):
  if parent_weight == 0:
    return 0
  return ((child_weight/float(parent_weight)) - ((inter_cluster_weight/float(parent_weight))*(inter_cluster_weight/float(parent_weight))))

# calculate modularity function Q
def calculate_Q(tag_co_occurrence_histogram, cluster1, cluster2):
  # A(V,V)
  parent_weight = calculate_parent_weight(tag_co_occurrence_histogram)
  print "Done calculate parent_weight"

  # A(Vc,Vc)
  child1_weight, child2_weight = calculate_child_weights(tag_co_occurrence_histogram, cluster1, cluster2)
  print "Done calculate child weights"

  # A(Vc,V)
  inter_cluster_child1_parent_weight, inter_cluster_child2_parent_weight = calculate_inter_cluster_weights(tag_co_occurrence_histogram, cluster1, cluster2)
  inter_cluster_child1_parent_weight += child1_weight
  inter_cluster_child2_parent_weight += child2_weight
  print "Done calculate inter cluster weights"

  # calculate modularity Q
  q1 = calculate_modularity_of_child_cluster(child1_weight, inter_cluster_child1_parent_weight, parent_weight)
  q2 = calculate_modularity_of_child_cluster(child2_weight, inter_cluster_child2_parent_weight, parent_weight)
  return q1 + q2

################     Recursive Partitioning       ###################################

def partitioning(tag_index_dict, tag_co_occurrence_histogram):
  # create laplace matrice
  laplace_matrix = calculate_laplace_matrix(tag_index_dict, tag_co_occurrence_histogram)
  print "Done creating laplace matrix"

  # create two overlapping clusters
  index_tag_dict = dict(zip(tag_index_dict.values(), tag_index_dict.keys()))
  cluster1, cluster2 = spectral_bisection(laplace_matrix, index_tag_dict)
  print "Done group into 2 child clusters"
  #pprint.pprint(cluster1)
  #pprint.pprint(cluster2)
  return cluster1, cluster2

def split_dictionary(dictionary, cluster1, cluster2):
  dict1 = dict()
  current_index1 = 0
  dict2 = dict()
  current_index2 = 0
  for key, value in dictionary.items():
    if key in cluster1:
      dict1[key] = current_index1
      current_index1 += 1
    if key in cluster2:
      dict2[key] = current_index2
      current_index2 += 1
  return dict1, dict2

def split_co_occurence_histogram(co_occurrence_histogram, cluster1, cluster2):
  # TODO
  co_occurrence_histogram1 = Counter()
  co_occurrence_histogram2 = Counter()
  for (tag1, tag2), value in co_occurrence_histogram.items():
    if tag1 in cluster1 and tag2 in cluster1:
      co_occurrence_histogram1[(tag1, tag2)] = value
    if tag1 in cluster2 and tag2 in cluster2:
      co_occurrence_histogram2[(tag1, tag2)] = value
  return co_occurrence_histogram1, co_occurrence_histogram2

def recursive_partitioning(tag_index_dict, tag_co_occurrence_histogram):
  tag_clusters = []
  cluster1, cluster2 = partitioning(tag_index_dict, tag_co_occurrence_histogram)
   # calculate modularity function Q whether partition is useful
  q = calculate_Q(tag_co_occurrence_histogram, cluster1, cluster2)
  print "Done calculate q: %f" % q
  print "######################     Done with one bisection        ###################################"
  if q > 0:
    tag_index_dict1, tag_index_dict2 = split_dictionary(tag_index_dict, cluster1, cluster2)
    #print tag_index_dict1
    #print tag_index_dict2
    tag_co_occurrence_histogram1, tag_co_occurrence_histogram2 = split_co_occurence_histogram(tag_co_occurrence_histogram, cluster1, cluster2)
    #print tag_co_occurrence_histogram1
    #print tag_co_occurrence_histogram2
    if len(cluster1) > 1:
      tag_clusters.extend(recursive_partitioning(tag_index_dict1, tag_co_occurrence_histogram1))
    if len(cluster2) > 1:
      tag_clusters.extend(recursive_partitioning(tag_index_dict2, tag_co_occurrence_histogram2))
  else:
    print "------------------------- Q < 0 ------------------------------"
    return [tag_index_dict.keys()]
  return tag_clusters

################     Photo Clustering  #############################

def intersect_tag_lists(tag_cluster,tag_list):
  return list(set(tag_cluster).intersection( set(tag_list) ))


def get_photo_clusters(tag_clusters,photo_tags_dict):
  affiliated_photos_tuples = []
  for tag_cluster in tag_clusters:
    affiliated_photos = {}
    for photo_id, tag_list in photo_tags_dict.items():
      if (not tag_list == None) and (len(tag_list) > 0):
        shared_tags = intersect_tag_lists(tag_cluster,tag_list)
        #print "Photo %d | shared tags = %d | shared_tags / photo_tags = %f | shared_tags / tag_cluster = %f" % (photo_id,len(shared_tags),len(shared_tags)/float(len(tag_list)),len(shared_tags)/float(len(tag_cluster)))
        if len(shared_tags) > 0:
          affiliation_score = len(shared_tags)/float(len(tag_list)) + len(shared_tags)/float(len(tag_cluster))
          affiliated_photos[photo_id] = affiliation_score
    sorted_affiliated_photos = sorted(affiliated_photos.iteritems(), key=operator.itemgetter(1))
    sorted_affiliated_photos.reverse()
    affiliated_photos_tuples.append(sorted_affiliated_photos)
    #print sorted_affiliated_photos
  return affiliated_photos_tuples




################     Main        ###################################

def main():
  number_of_jsons = 100

  tag_co_occurrence_histogram, tag_index_dict, photo_tags_dict, photo_data_list = tag_preprocessing(number_of_jsons);

  tag_clusters = recursive_partitioning(tag_index_dict, tag_co_occurrence_histogram)
  for tag_cluster in tag_clusters:
    print tag_cluster
  print "%d clusters" % len(tag_clusters)

  # cluster photos
  print "Calculate photo clusters"
  photo_clusters = get_photo_clusters(tag_clusters,photo_tags_dict)
  print "Done"

  # write clusters to html
  clusters = defaultdict(list)
  additional_columns= {}
  additional_columns["Tags"] = []
  for index, cluster in enumerate(photo_clusters):
    additional_columns["Tags"].append(tag_clusters[index])
    for photo_id, score in cluster:
      clusters[index].append(dict(photo_data_list[photo_id].items()+{"score":score}.items()))

  name_of_html_file = str(number_of_jsons) + "_old_q_second_smallest.html"
  write_clusters_to_html(clusters, html_file_path=name_of_html_file, additional_columns=additional_columns, open_in_browser=True)

if __name__ == '__main__':
    main()
