#!/usr/bin/python
# -*- coding: utf-8 -*-

######################################################################################
# Calculates the tf-idf for co occurring tags and synsets
#
#
# authors: mandy roick
# mail: mandy.roick@student.hpi.uni-potsdam.de
######################################################################################

from collections import defaultdict
from math import log

def calculate_normalization_factors(synset_filenames_dict, unmatched_tag_filenames_dict):
  # create data structures for collecting normalization factors
  synset_tag_co_occurrence_dict = dict()
  max_co_occurrence_for_synset = dict()
  how_many_synsests_for_tag = dict()
  for unmatched_tag in unmatched_tag_filenames_dict.keys():
    how_many_synsests_for_tag[unmatched_tag] = 0

  # first run over the data to find normalization factors
  for synset, synset_filenames in synset_filenames_dict.iteritems():
    max_co_occurrence_for_synset[synset] = 0
    for unmatched_tag, unmatched_tag_filenames in unmatched_tag_filenames_dict.iteritems():
      co_occurence = len(set(synset_filenames).intersection(set(unmatched_tag_filenames)))
      if co_occurence > max_co_occurrence_for_synset[synset]:
        max_co_occurrence_for_synset[synset] = co_occurence
      if co_occurence > 0:
        how_many_synsests_for_tag[unmatched_tag] += 1
        synset_tag_co_occurrence_dict[(synset, unmatched_tag)] = co_occurence

  how_many_synsets = len(synset_filenames_dict.keys())

  return (synset_tag_co_occurrence_dict, max_co_occurrence_for_synset, how_many_synsests_for_tag, how_many_synsets)


def calculate_tf_idfs(normalization_factors):
  synset_tag_co_occurrence_dict, max_co_occurrence_for_synset, how_many_synsests_for_tag, how_many_synsets = normalization_factors
  synset_tags_tf_idf_dict = defaultdict(list)
  max_tf_idf = 0

  # second run to actually calculate the tf idfs
  for (synset, unmatched_tag), co_occurence in synset_tag_co_occurrence_dict.iteritems():
    tf = 0
    idf = 0
    if max_co_occurrence_for_synset[synset] != 0:
      tf = co_occurence/float(max_co_occurrence_for_synset[synset])
    if how_many_synsests_for_tag[unmatched_tag] != 0:
      idf =  log(how_many_synsets/float(how_many_synsests_for_tag[unmatched_tag]))
    tf_idf = tf*idf
    if tf_idf > max_tf_idf:
      max_tf_idf = tf_idf
    synset_tags_tf_idf_dict[synset].append((unmatched_tag, tf_idf))

  return (max_tf_idf, synset_tags_tf_idf_dict)


def create_unmatched_tag_tf_idf_dict(synset_filenames_dict,unmatched_tag_filenames_dict):
  normalization_factors = calculate_normalization_factors(synset_filenames_dict, unmatched_tag_filenames_dict)
  max_tf_idf, synset_tags_tf_idf_dict = calculate_tf_idfs(normalization_factors)

  return (max_tf_idf, synset_tags_tf_idf_dict)