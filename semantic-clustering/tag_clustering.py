#!/usr/bin/python
# -*- coding: utf-8 -*-

######################################################################################
# Clusters the given tags
#
#
# authors: tino junge, mandy roick
# mail: tino.junge@student.hpi.uni-potsdam.de, mandy.roick@student.hpi.uni-potsdam.de
######################################################################################

import numpy as np
from scipy import linalg
from collections import Counter

tag_co_occurrence_histogram = Counter()

################     Laplace Matrix       ###################################

def calculate_negative_adjacency_matrix(tag_list):
  negative_adjacency_matrix = np.zeros((len(tag_list),len(tag_list)))
  for index1 in range(0, len(tag_list)):
    for index2 in range(index1, len(tag_list)):
      if ((tag_list[index1], tag_list[index2]) in tag_co_occurrence_histogram) or ((tag_list[index2], tag_list[index1]) in tag_co_occurrence_histogram):
        negative_adjacency_matrix[index1][index2] = -1
        negative_adjacency_matrix[index2][index1] = -1
  return negative_adjacency_matrix

# set diagonal of laplace to degrees of vertices
def add_diagonal_matrix_to_adjacency(matrix):
  for i,line in enumerate(matrix):
    matrix[i][i] = sum(line)*(-1)
  return matrix

def calculate_laplace_matrix(tag_list):
  laplace_matrix = calculate_negative_adjacency_matrix(tag_list)
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

def create_clusters(partitioning_vector, tag_list):
  tag_cluster1 = []
  tag_cluster2 = []

  # '>=' instead of '>' results in overlapping clusters
  for index, vector_value in enumerate(partitioning_vector):
    if vector_value > 0:
      tag_cluster1.append(tag_list[index])
    if vector_value < 0:
      tag_cluster2.append(tag_list[index])

  return tag_cluster1, tag_cluster2

def spectral_bisection(matrix, tag_list):
  eigen_values, eigen_vectors = linalg.eig(matrix)
  print "Done calculate eigenvalues"
  partitioning_vector = calculate_second_smallest_eigen_vector(eigen_values, eigen_vectors)
  print "Done find vector for second highest eigenvalue"
  return create_clusters(partitioning_vector, tag_list)


################     Calculate Q       ###################################

def calculate_parent_weight():
  return 2*sum(tag_co_occurrence_histogram.values())

def calculate_child_weights(cluster1, cluster2):
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

def calculate_inter_cluster_weights(cluster1, cluster2):
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
def calculate_Q(cluster1, cluster2):
  # A(V,V)
  parent_weight = calculate_parent_weight()
  print "Done calculate parent_weight"

  # A(Vc,Vc)
  child1_weight, child2_weight = calculate_child_weights(cluster1, cluster2)
  print "Done calculate child weights"

  # A(Vc,V)
  inter_cluster_child1_parent_weight, inter_cluster_child2_parent_weight = calculate_inter_cluster_weights(cluster1, cluster2)
  inter_cluster_child1_parent_weight += child1_weight
  inter_cluster_child2_parent_weight += child2_weight
  print "Done calculate inter cluster weights"

  # calculate modularity Q
  q1 = calculate_modularity_of_child_cluster(child1_weight, inter_cluster_child1_parent_weight, parent_weight)
  q2 = calculate_modularity_of_child_cluster(child2_weight, inter_cluster_child2_parent_weight, parent_weight)
  return q1 + q2


################     Recursive Partitioning       ###################################

def partitioning(tag_list):
  # create laplace matrix
  laplace_matrix = calculate_laplace_matrix(tag_list)
  print "Done creating laplace matrix"

  # create two not overlapping clusters
  cluster1, cluster2 = spectral_bisection(laplace_matrix, tag_list)
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

def recursive_partitioning(tag_list):
  tag_clusters = []
  cluster1, cluster2 = partitioning(tag_list)
   # calculate modularity function Q whether partition is useful
  q = calculate_Q(cluster1, cluster2)
  print "Done calculate q: %f" % q
  print "######################     Done with one bisection        ###################################"
  if q > 0:
    if len(cluster1) > 1:
      tag_clusters.extend(recursive_partitioning(cluster1))
    else:
      tag_clusters.append(cluster1)
    if len(cluster2) > 1:
      tag_clusters.extend(recursive_partitioning(cluster2))
    else:
      tag_cluster.append(cluster2)
  else:
    print "------------------------- Q < 0 ------------------------------"
    return [tag_list]
  return tag_clusters


################     Tag Clustering       ###################################

def tag_clustering(tag_index_dict, co_occurrence_histogram):
  global tag_co_occurrence_histogram
  tag_co_occurrence_histogram = co_occurrence_histogram
  tag_clusters = recursive_partitioning(tag_index_dict.keys())

  for tag_cluster in tag_clusters:
    print tag_cluster
  print "%d clusters" % len(tag_clusters)

  return tag_clusters