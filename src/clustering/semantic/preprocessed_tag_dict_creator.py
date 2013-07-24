#!/usr/bin/python
# -*- coding: utf-8 -*-

#########################################################################################
# Create picture and synset/tag dictionaries and write them on disk
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
from clustering.semantic.synset_detection_bestfirstsearch import *
from clustering.semantic.mcl_keyword_clustering import keyword_clustering_via_mcl

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

def parse_command_line_arguments():
  parser = argparse.ArgumentParser()
  parser.add_argument('-m','--withmcl', dest='create_mcl_clusters', action='store_true',
                      help='If specified, cluster keywords with mcl, otherwise leave it out and be windows friendly')
  parser.add_argument('-n','--number_of_jsons', dest='number_of_jsons', type=int,
                      help='Specifies the number of jsons which will be processed')
  args = parser.parse_args()
  return args

def main():
  arguments = parse_command_line_arguments()

  if arguments.number_of_jsons:
    number_of_jsons = arguments.number_of_jsons
  else:
    # Default if not in arguments
    number_of_jsons = 100
    print "Default: Running with %d json files" % number_of_jsons

  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  synset_tag_tf_idf_dict_filename = config.get('Filenames for Pickles', 'synset-tag-cooccurrence-dict')
  keywords_for_pictures_filename = config.get('Filenames for Pickles', 'keywords_for_pictures_filename')
  synset_filenames_dict_filename = config.get('Filenames for Pickles', 'synset_filenames_dict_filename')
  unmatched_tag_filenames_dict_filename = config.get('Filenames for Pickles', 'unmatched_tag_filenames_dict_filename')

  keywords_for_pictures_all = {}
  for keywords_for_pictures in find_metajsons_to_process_in_dir(keywords_for_pictures_dir):
    keywords_for_pictures_all.extend(keywords_for_pictures)

  print_status("Writing keywords_for_pictures... ")
  keywords_for_pictures_filename.replace('##', 'all')
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

  if arguments.create_mcl_clusters:
    print_status("Create MCL clusters and write them to file... \n")
    keyword_clustering_via_mcl(storable_synset_filenames_dict)
    print_status("Done.\n")

if __name__ == '__main__':
    main()
