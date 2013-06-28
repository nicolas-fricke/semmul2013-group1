#!/usr/bin/python
# -*- coding: utf-8 -*-

######################################################################################
#
# Search the given word in wordnet and try to cluster images which belongs to it
#
#
# authors: claudia.exeler, mandy.roick
# mail: {claudia.exeler mandy.roick}@student.hpi.uni-potsdam.de
######################################################################################

import ConfigParser
import operator
from collections import Counter, defaultdict
from subprocess import call
from nltk.corpus import wordnet as wn

from helpers.general_helpers import *

################ create keyword clusters ##############################

def get_synset_co_occurrence_dict(synset_filenames_dict):
  co_occurrence_dict = dict()
  max_co_occurrence = 0
  for synset1, filenames1 in synset_filenames_dict.iteritems():
    for synset2, filenames2 in synset_filenames_dict.iteritems():
      if synset1 < synset2:
        #if (synset1.name, synset2.name) not in co_occurrence_dict:
        co_occurence = len(set(filenames1).intersection(set(filenames2)))
        co_occurrence_dict[(synset1, synset2)] = co_occurence
        if co_occurence > max_co_occurrence:
          max_co_occurrence = co_occurence
  return max_co_occurrence, co_occurrence_dict

def calculate_edge_weigthings_for_synsets(synset_filenames_dict):
  max_co_occurrence, co_occurrence_dict = get_synset_co_occurrence_dict(synset_filenames_dict)

  edge_weigthings_for_synsets = dict()
  for synset1, filenames1 in synset_filenames_dict.iteritems():
    for synset2, filenames2 in synset_filenames_dict.iteritems():
      if synset1 < synset2:
        #if (synset1.name, synset2.name) not in similarity_histogram:
        similarity = wn.synset(synset1).lch_similarity(wn.synset(synset2))
        co_occurrence = co_occurrence_dict[(synset1, synset2)] / float(max_co_occurrence)
        if similarity < 1.8:
          similarity = 0
        edge_weigthings_for_synsets[(synset1, synset2)] = similarity + 2*co_occurrence
  return edge_weigthings_for_synsets

def write_edge_weightings_to_file(edge_weigthings_for_synsets, file_name):
  print "Writing edge weighting to mcl readable file."
  output_file = open(file_name, 'w')
  for (synset1, synset2), edge_weighting in edge_weigthings_for_synsets.iteritems():
    output_file.write(str(synset1) + ' ' + str(synset2) + ' ' + str(edge_weighting) + '\n')
  output_file.close()

def mcl_clustering(edge_weightings):
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  mcl_filename = config.get('Filenames for Pickles', 'mcl_clusters_filename')

  edge_weightings_filename = 'edge_weightings_for_mcl.txt'
  write_edge_weightings_to_file(edge_weightings, edge_weightings_filename)

  call(["mcl", edge_weightings_filename, "--abc", "-o", mcl_filename])

def keyword_clustering_via_mcl(synset_filenames_dict):
  edge_weigthings_for_synsets = calculate_edge_weigthings_for_synsets(synset_filenames_dict)
  mcl_clustering(edge_weigthings_for_synsets)

################ create picture clusters ##############################

def read_clusters_from_file(file_name):
  cluster_for_synsets = dict()
  cluster_file = open(file_name, 'r')
  for number_of_cluster, line in enumerate(cluster_file):
    for synset in line.rstrip('\n\r').split('\t'):
      cluster_for_synsets[synset] = number_of_cluster
  cluster_file.close()
  return cluster_for_synsets


def get_clusters_with_highest_counter(cluster_counter):
  result = []
  sorted_cluster_counter = sorted(cluster_counter.items(), key=operator.itemgetter(1), reverse=True)
  result.append(sorted_cluster_counter[0][0])

  max_count = sorted_cluster_counter[0][1]
  i = 0
  while sorted_cluster_counter[i][1] == max_count:
    result.append(sorted_cluster_counter[i][0])
    i += 1
    if i >= len(sorted_cluster_counter):
      break
  return result


def cluster_via_mcl(searchtree):
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  mcl_filename = config.get('Filenames for Pickles', 'mcl_clusters_filename')
  keywords_for_pictures_filename = config.get('Filenames for Pickles', 'keywords_for_pictures_filename')

  cluster_for_synsets = read_clusters_from_file(mcl_filename)
  url_and_keywords_for_pictures = load_object(keywords_for_pictures_filename)
  pictures_for_clusters = defaultdict(list)

  for picture in searchtree.associated_pictures:
    cluster_counter = Counter()
    synsets_for_picture = url_and_keywords_for_pictures[picture[0]][1]
    for synset in synsets_for_picture:
      try: 
        cluster_counter[cluster_for_synsets[synset]] += 1
      except KeyError:
        continue
    if len(cluster_counter) > 0:
      for synset_cluster_number in get_clusters_with_highest_counter(cluster_counter):
        pictures_for_clusters[synset_cluster_number].append(picture)
    else:
      #TODO: where to put unassignable pictures?
      pictures_for_clusters[0].append(picture)

  searchtree.subclusters = pictures_for_clusters.values()
  if len(searchtree.associated_pictures) > 0:
    print "%s has %d subclusters." % (searchtree.name, len(searchtree.subclusters)) 

  # Recursively traverse tree
  if searchtree.has_hyponyms():
    for child_hyponym_node in searchtree.hyponyms:
      cluster_via_mcl(child_hyponym_node)
  if searchtree.has_meronyms():
    for child_meronym_node in searchtree.meronyms:
      cluster_via_mcl(child_meronym_node)
  
  return searchtree