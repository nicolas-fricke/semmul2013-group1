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

import ConfigParser
from collections import Counter
import json
import glob
import pprint
import nltk
from nltk.corpus import wordnet as wn
import numpy as np
from scipy import linalg

################     Reading of Files       ####################################

# probably add preprocessing steps for tags
def read_tags_from_json(json_data):
  tag_list = []
  for raw_tag in json_data["metadata"]["info"]["tags"]["tag"]:
    # Preprocess tag before appending to tag_list
    tag = raw_tag["_content"]
    #tag = tag.lower               # Only lower case
    #tag = wn.morphy(tag)          # Stemmming
    tag_list.append(tag)
  return tag_list

def get_json_files(metadata_dir):
  return glob.glob(metadata_dir + '/*/*/10000*.json')

def read_tags_from_file(json_file):
  f = open(json_file)
  json_data = json.load(f)
  f.close()
  tag_list = []
  if json_data["stat"] == "ok":
    return read_tags_from_json(json_data)
  return None

def import_metadata_dir_of_config(path):
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  return '../' + config.get('Directories', 'metadata-dir')

def calculate_tag_histogram_and_co_occurence_histogram(json_files):
  tag_histogram = Counter()
  tag_co_occurrence_histogram = Counter()
  for json_file in json_files:
    tag_list = read_tags_from_file(json_file)
    if not tag_list == None:
      tag_histogram.update(tag_list)
      tag_co_occurrence_histogram.update([(tag1,tag2) for tag1 in tag_list for tag2 in tag_list if tag1 < tag2])
  return tag_histogram, tag_co_occurrence_histogram

################     Tag Clustering       ####################################

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
  laplace_matrix = add_diagonal_matrix_to_adjacency(laplace_matrix)
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

def create_clusters(separation_vector, index_tag_dict):
  tag_cluster1 = []
  tag_cluster2 = []

  # '>=' instead of '>' results in overlapping clusters
  for index, vector_value in enumerate(separation_vector):
    if vector_value >= 0:
      tag_cluster1.append(index_tag_dict[index])
    if vector_value <= 0:
      tag_cluster2.append(index_tag_dict[index])

  return tag_cluster1, tag_cluster2

def sepctral_bisection(matrix, index_tag_dict):
  eigen_values, eigen_vectors = linalg.eig(matrix)
  print "\t Done calculate eigenvalues"
  second_highest_eigen_vector = calculate_second_highest_eigen_vector(eigen_values, eigen_vectors)
  print "\t Done find vector for second highest eigenvalue"
  return create_clusters(second_highest_eigen_vector, index_tag_dict)

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

def main():
  # import configuration
  metadata_dir = import_metadata_dir_of_config('../config.cfg')

  # read json files from metadata directory
  json_files = get_json_files(metadata_dir)
  print "Done Reading " + str(len(json_files)) + " Json Files"

  tag_histogram, tag_co_occurrence_histogram = calculate_tag_histogram_and_co_occurence_histogram(json_files)
  print "Done histogram creation. %2d Tags" % len(tag_histogram)

  # initialize tag dictionary
  tag_dict = dict()
  for i, key in enumerate(tag_histogram.keys()):
    tag_dict[key] = i
  print "Done Tag Dict"
  #print tag_dict

  # create laplace matrice
  laplace_matrix = calculate_laplace_matrix(tag_dict, tag_co_occurrence_histogram)
  print "Done creating laplace matrix"

  # create two overlapping clusters
  index_tag_dict = dict(zip(tag_dict.values(), tag_dict.keys()))
  cluster1, cluster2 = sepctral_bisection(laplace_matrix, index_tag_dict)
  print "Done group into 2 child clusters"
  #pprint.pprint(cluster1)
  #pprint.pprint(cluster2)

  q = calculate_Q(tag_co_occurrence_histogram, cluster1, cluster2)
  print "Done calculate q: " + str(q)

if __name__ == '__main__':
    main()
