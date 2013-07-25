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

from helpers.general_helpers import print_status, read_clusters_from_file, read_cluster_representatives, load_object
from helpers.general_helpers import load_cluster_for_synsets, load_keywords_for_pictures, load_synset_filenames_dict

################ create keyword clusters ##############################

def calculate_max_co_occurrence(synset_filenames_dict):
  max_co_occurrence = 0
  for synset1, filenames1 in synset_filenames_dict.iteritems():
    for synset2, filenames2 in synset_filenames_dict.iteritems():
      if synset1 < synset2:
        co_occurence = len(set(filenames1).intersection(set(filenames2)))
        if co_occurence > max_co_occurrence:
          max_co_occurrence = co_occurence
  return max_co_occurrence

def calculate_and_write_edge_weigthings_for_synsets(synset_filenames_dict, file_name):
  max_co_occurrence = calculate_max_co_occurrence(synset_filenames_dict)
  edge_weigthings_for_synsets = dict()
  how_many_added = 0
  how_many_done = 0
  how_many_to_do = len(synset_filenames_dict.keys()) * (len(synset_filenames_dict.keys())-1)
  write_edge_weightings_to_file(dict(), file_name)

  for synset1, filenames1 in synset_filenames_dict.iteritems():
    for synset2, filenames2 in synset_filenames_dict.iteritems():
      if synset1 < synset2:
        how_many_done += 1
        #if (synset1.name, synset2.name) not in similarity_histogram:
        similarity = wn.synset(synset1).lch_similarity(wn.synset(synset2))
        co_occurence = len(set(synset_filenames_dict[synset1]).intersection(set(synset_filenames_dict[synset2])))
        normalized_co_occurrence = co_occurence/max_co_occurrence
        if similarity < 2.0:
          similarity = 0
        if normalized_co_occurrence < 0.4:
          normalized_co_occurrence = 0
        edge_weighting = similarity + 4*normalized_co_occurrence
        if edge_weighting != 0:
          edge_weigthings_for_synsets[(synset1, synset2)] = edge_weighting
          how_many_added += 1
        if how_many_added > 1000:
          print_status("Done with " + str(how_many_done) + " von " + str(how_many_to_do) + "\n")
          write_edge_weightings_to_file(edge_weigthings_for_synsets, file_name, append_to_file=True)
          edge_weigthings_for_synsets = dict()
          how_many_added = 0
  write_edge_weightings_to_file(edge_weigthings_for_synsets, file_name, append_to_file=True)

def write_edge_weightings_to_file(edge_weigthings_for_synsets, file_name, append_to_file=False):
  print_status("Writing edge weightings to mcl readable file.")
  output_file = None
  if append_to_file:
    output_file = open(file_name, 'a')
  else:
    output_file = open(file_name, 'w')
  for (synset1, synset2), edge_weighting in edge_weigthings_for_synsets.iteritems():
    output_file.write(str(synset1) + ' ' + str(synset2) + ' ' + str(edge_weighting) + '\n')
  output_file.close()
  print "Done."

def mcl_clustering(edge_weightings_filename):
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  mcl_filename = config.get('Filenames for Pickles', 'mcl_clusters_filename')
  edge_weightings_filename = config.get('Filenames for Pickles', 'edge_weightings_filename')

  call(["mcl", edge_weightings_filename, "--abc", "-o", mcl_filename])

def keyword_clustering_via_mcl(synset_filenames_dict):
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  edge_weightings_filename = config.get('Filenames for Pickles', 'edge_weightings_filename')

  calculate_and_write_edge_weigthings_for_synsets(synset_filenames_dict, edge_weightings_filename)
  print_status("Done calculation of edge weightings and writing to file.\n")

  print_status("Start MCL Clustering...")
  mcl_clustering(edge_weightings_filename)
  print "Done."

################ create picture clusters ##############################

filenames_for_synsets_global = None

def get_clusters_with_highest_counter(cluster_counter):
  result = []
  sorted_cluster_counter = sorted(cluster_counter.items(), key=operator.itemgetter(1), reverse=True)
  max_count = sorted_cluster_counter[0][1]

  i = 0
  while sorted_cluster_counter[i][1] == max_count:
    result.append(sorted_cluster_counter[i][0])
    i += 1
    if i >= len(sorted_cluster_counter):
      break
  return result

def compare_representatives(x,y):
  return cmp(len(filenames_for_synsets_global[x]),len(filenames_for_synsets_global[y]))

def find_best_representatives():
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  mcl_filename = config.get('Filenames for Pickles', 'mcl_clusters_filename')
  cluster_representatives = read_cluster_representatives(mcl_filename)
  best_cluster_representatives = []
  for cluster in cluster_representatives:
    sorted_cluster_representatives = sorted(cluster, cmp=compare_representatives, reverse=True)
    if len(sorted_cluster_representatives) < 7:
      best_cluster_representatives.append(sorted_cluster_representatives)
    else:
      best_cluster_representatives.append(sorted_cluster_representatives[:6]) 
  return best_cluster_representatives


def cluster_via_mcl(searchtree, mcl_clustering_threshold=2, minimal_mcl_cluster_size=2, cluster_for_synsets=None, 
                    url_and_keywords_for_pictures=None, filenames_for_synsets=None, best_cluster_representatives=None):
  if cluster_for_synsets == None:
    cluster_for_synsets = load_cluster_for_synsets()
  if url_and_keywords_for_pictures == None:
    url_and_keywords_for_pictures = load_keywords_for_pictures()
  if filenames_for_synsets_global == None and filenames_for_synsets == None:
    filenames_for_synsets = load_synset_filenames_dict()
  if filenames_for_synsets_global == None:
    global filenames_for_synsets_global
    filenames_for_synsets_global = filenames_for_synsets

  if best_cluster_representatives == None:
    best_cluster_representatives = find_best_representatives()

  pictures_for_clusters = defaultdict(list)
  subcluster_list = []

  if len(searchtree.associated_pictures) >= mcl_clustering_threshold:
    
    # cluster pictures via mcl
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
          pictures_for_clusters[synset_cluster_number+1].append(picture)
      else:
        print "unassignable picture: ", picture[0]
        pictures_for_clusters[0].append(picture)

    # eliminate clusters which are subclusters of other clusters
    # len_sorted_pictures = sorted(iterable)
    for key, pictures in pictures_for_clusters.iteritems():
      if len(pictures) >= minimal_mcl_cluster_size:
        is_subset = False
        for subcluster in subcluster_list:
          is_subset_candidate = True
          for picture in pictures:
            if picture not in subcluster["subcluster"]:
              is_subset_candidate = False
              break
          if is_subset_candidate:
            is_subset = True
            break
        if not is_subset:
          # print str(key) + ", "
          subcluster_list.append({"synsets": best_cluster_representatives[key], "subcluster": pictures})

    searchtree.subclusters = subcluster_list
  else:
    searchtree.subclusters = [{"synsets": None, "subcluster": searchtree.associated_pictures}]

  # Recursively traverse tree
  if searchtree.has_hyponyms():
    for child_hyponym_node in searchtree.hyponyms:
      cluster_via_mcl(child_hyponym_node, mcl_clustering_threshold, minimal_mcl_cluster_size, 
                      cluster_for_synsets, url_and_keywords_for_pictures, filenames_for_synsets, best_cluster_representatives)
  if searchtree.has_meronyms():
    for child_meronym_node in searchtree.meronyms:
      cluster_via_mcl(child_meronym_node, mcl_clustering_threshold, minimal_mcl_cluster_size, 
                      cluster_for_synsets, url_and_keywords_for_pictures, filenames_for_synsets, best_cluster_representatives)

  return searchtree