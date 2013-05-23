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
  return glob.glob(metadata_dir + '/*/*/1000*.json')

def read_tags_from_file(json_file):
  f = open(json_file)
  json_data = json.load(f)
  f.close()
  tag_list = []
  if json_data["stat"] == "ok":
    return read_tags_from_json(json_data)
  return None

def main():
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  metadata_dir = '../' + config.get('Directories', 'metadata-dir')

  # read json files from metadata directory
  json_files = get_json_files(metadata_dir)
  print "Done Reading " + str(len(json_files)) + " Json Files"

  # get list of all tags and count there co-occurrences
  tag_histogram = Counter()
  tag_co_occurrence_histogram = Counter()
  for json_file in json_files:
    tag_list = read_tags_from_file(json_file)
    if not tag_list == None:
      tag_histogram.update(tag_list)
      tag_co_occurrence_histogram.update([(tag1,tag2) for tag1 in tag_list for tag2 in tag_list if tag1 < tag2])
  #print tag_histogram
  #print tag_co_occurrence_histogram
  print "Done histogram creation. %2d Tags" % len(tag_histogram)

  # initialize tag dictionary
  tag_dict = dict()
  for i, key in enumerate(tag_histogram.keys()):
    tag_dict[key] = i
  print "Done Tag Dict"
  #print tag_dict

  # create laplace matrice
  laplace_matrice = np.zeros((len(tag_histogram),len(tag_histogram)))
  for (tag1, tag2) in tag_co_occurrence_histogram:
    laplace_matrice[tag_dict[tag1]][tag_dict[tag2]] = -1
    laplace_matrice[tag_dict[tag2]][tag_dict[tag1]] = -1
  print "Done creating laplace_matrice"

  # create diagonal matrice with degree of vertices
  for i,line in enumerate(laplace_matrice):
    laplace_matrice[i][i] = sum(line)*(-1)
  np.set_printoptions(threshold='nan')
  print "Done creating diagonal matrice"
  #print  laplace_matrice

  # calculate second highest eigenvalue and eigenvector of laplace_matrice
  e_vals, e_vecs = linalg.eig(laplace_matrice)
  #print np.linalg.eig(laplace_matrice)
  highest_eval = 0
  highest_index = 0
  sec_highest_eval = 0
  sec_highest_index = 0
  for i,e_val in enumerate(e_vals):
    if e_val > highest_eval:
      sec_highest_eval = highest_eval
      sec_highest_index = highest_index
      highest_eval = e_val
      highest_index = i
    elif e_val > sec_highest_eval:
      sec_highest_eval = e_val
      sec_highest_index = i

  sec_highest_evec = e_vecs[sec_highest_index]
  print "Done calculating sec_highest_eval"
  #print "Highest e_val, e_vec"
  #print highest_eval ,  e_vecs[highest_index]
  #print "Second Highest e_val, e_vec"
  #print sec_highest_eval , e_vecs[sec_highest_index]

  # create inverse tag_dict for accesing tags through index
  tag_dict_reverse = dict(zip(tag_dict.values(), tag_dict.keys()))
  print "Done creating tag_dict_reverse"

  # group tags in 2 clusters corresponding to their value in the second highest eigenvector (<0 and >0, =0 in both clusters)
  cluster1 = []
  cluster2 = []
  for i,val in enumerate(sec_highest_evec):
    if val > 0:
      cluster1.append(tag_dict_reverse[i])
    elif val < 0:
      cluster2.append(tag_dict_reverse[i])
    elif val == 0:
      cluster1.append(tag_dict_reverse[i])
      cluster2.append(tag_dict_reverse[i])

  print "Done group into 2 child cluster"
  #pprint.pprint(cluster1)
  #pprint.pprint(cluster2)

  # calculate modularity function Q
  # --------------------------------------------
  # sum up edge weights of parent cluster A(V,V)
  parent_weight = 2*sum(tag_co_occurrence_histogram.values())
  print "Done calculate parent_weight"

  # sum up edge weights of two child clusters A(Vc,Vc)
  child1_weight = 0
  child2_weight = 0
  for (tag1, tag2), weight in tag_co_occurrence_histogram.items():
    if tag1 in cluster1 and tag2 in cluster1:
      child1_weight += weight
    if tag1 in cluster2 and tag2 in cluster2:
      child2_weight += weight

  child1_weight *= 2
  child2_weight *= 2
  print "Done calculate child weights"
  #print "child1_weight %2d" % child1_weight
  #print "child2_weight %2d" % child2_weight

  # sum up edge weight for intra cluster weights A(Vc,V)
  intra_cluster_child1_parent_weight = 0
  intra_cluster_child2_parent_weight = 0
  for (tag1, tag2), weight in tag_co_occurrence_histogram.items():
    if tag1 in cluster1 and tag2 in cluster2:
      intra_cluster_child1_parent_weight += weight
    if tag1 in cluster2 and tag2 in cluster1:
      intra_cluster_child2_parent_weight += weight

  intra_cluster_child1_parent_weight += child1_weight
  intra_cluster_child2_parent_weight += child2_weight

  # calculate modularity Q
  q1 = child1_weight/parent_weight - ((intra_cluster_child1_parent_weight/parent_weight)*(intra_cluster_child1_parent_weight/parent_weight))
  q2 = child2_weight/parent_weight - ((intra_cluster_child2_parent_weight/parent_weight)*(intra_cluster_child2_parent_weight/parent_weight))
  q = q1 + q2

  print q

if __name__ == '__main__':
    main()
