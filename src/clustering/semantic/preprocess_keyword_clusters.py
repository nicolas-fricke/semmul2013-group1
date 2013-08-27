#!/usr/bin/python
# -*- coding: utf-8 -*-

#########################################################################################
# Create picture and synset/tag dictionaries and write them on disk
#
# usage: python preprocess_keyword_clusters.py
#
# filename -> list(synsets) list(tags) url
# synset -> list(filename,url)
# tag -> list(filename,url)
# synset -> list(tag,tf_idf)
#
# authors: tino junge, claudia exeler, mandy roick
# mail: tino.junge@student.hpi.uni-potsdam.de, claudia.exeler@student.hpi.uni-potsdam.de,
#       mandy.roick@student.hpi.uni-potsdam.de
#########################################################################################

from collections import defaultdict
import ConfigParser
import argparse
import gc

# Import own modules
from helpers.general_helpers import *

from clustering.semantic.co_occurrence_detection import create_unmatched_tag_tf_idf_dict
from clustering.semantic.preprocess_synset_detection_bestfirstsearch import *
from clustering.semantic.mcl_keyword_clustering import keyword_clustering_via_mcl, sorted_cluster_representatives

def create_inverse_keywords_for_pictures_dict(keywords_for_pictures):
  synset_filenames_dict = defaultdict(list)
  unmatched_tag_filenames_dict = defaultdict(list)
  for filename, (url, synset_list, unmatched_tags) in keywords_for_pictures.iteritems():
    for synset in synset_list:
      if (filename, url) not in synset_filenames_dict[synset]:
        synset_filenames_dict[synset].append((filename,url))
    for unmatched_tag in unmatched_tags:
      unmatched_tag_filenames_dict[unmatched_tag].append((filename,url))
  return synset_filenames_dict, unmatched_tag_filenames_dict

def calculate_and_write_tf_idf_dict(synset_filenames_dict, unmatched_tag_filenames_dict, tf_idf_dict_filename):
  tf_idfs_dict = create_unmatched_tag_tf_idf_dict(synset_filenames_dict, unmatched_tag_filenames_dict)
  print len(tf_idfs_dict[1].keys())

  write_json_file(tf_idfs_dict, tf_idf_dict_filename)

def main():
    # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  synset_tag_tf_idf_dict_filename = config.get('Filenames for Pickles', 'synset-tag-cooccurrence-dict')
  keywords_for_pictures_filename = config.get('Filenames for Pickles', 'keywords_for_pictures_filename')
  synset_filenames_dict_filename = config.get('Filenames for Pickles', 'synset_filenames_dict_filename')
  unmatched_tag_filenames_dict_filename = config.get('Filenames for Pickles', 'unmatched_tag_filenames_dict_filename')
  keywords_for_pictures_dir = config.get('Filenames for Pickles', 'keywords-for-pictures-dir')

  print_status("Collecting keywords_for_pictures... ")
  keywords_for_pictures_all = dict()
  for keywords_for_pictures_json in find_jsons_in_dir(keywords_for_pictures_dir):
    keywords_for_pictures = parse_json_file(keywords_for_pictures_json)
    keywords_for_pictures_all.update(keywords_for_pictures)
  print "Done."

  print_status("Writing keywords_for_pictures... ")
  keywords_for_pictures_filename = keywords_for_pictures_filename.replace('##', 'all')
  write_json_file(keywords_for_pictures_all, keywords_for_pictures_filename)
  print "Done."

  print_status("Create_inverse_keywords_for_pictures_dicts... ")
  storable_synset_filenames_dict, unmatched_tag_filenames_dict = create_inverse_keywords_for_pictures_dict(keywords_for_pictures_all)
  print "Done"

  print_status("Writing synset_filenames_dict... ")
  write_json_file(storable_synset_filenames_dict, synset_filenames_dict_filename)
  print "Done."

  print_status("Writing unmatched_tag_filenames_dict... ")
  write_json_file(unmatched_tag_filenames_dict, unmatched_tag_filenames_dict_filename)
  print "Done."

  print_status("Calculate and write tf_idf dictionary...")
  calculate_and_write_tf_idf_dict(storable_synset_filenames_dict, unmatched_tag_filenames_dict, synset_tag_tf_idf_dict_filename)
  print "Done."

  print_status("Collecting the garbage... ")
  gc.collect()
  print "Done."

  print_status("Create MCL clusters and write them to file... \n")
  keyword_clustering_via_mcl(storable_synset_filenames_dict)
  print_status("Done.\n")

  print_status("Sort mcl clusters according to synset frequencies... \n")
  sorted_cluster_representatives(storable_synset_filenames_dict)
  print_status("Done.\n")

if __name__ == '__main__':
    main()
