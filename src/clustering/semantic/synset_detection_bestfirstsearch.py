import argparse
import ConfigParser
import json
import bisect
from nltk.corpus import wordnet as wn
from collections import defaultdict
import operator
import os.path
from copy import deepcopy

# Import own modules
import sys
from helpers.general_helpers import *
from clustering.semantic.tag_preprocessing import *

def copy_path(synset_list):
  new_path = []
  for synset in synset_list:
    new_path.append(synset)
  return new_path

def calculate_current_distance(synset_in_question, assumed_synsets, current_distance):
  for synset in assumed_synsets:
    current_distance += (3.7 - synset_in_question.lch_similarity(synset))
  return current_distance

def extend_best_path(possible_paths, indefinite_synsets):
  possible_paths.sort()
  if len(possible_paths) > 100:
    possible_paths = possible_paths[:100]
  if possible_paths[0][2] >= len(indefinite_synsets):
    return possible_paths, True

  #print "extending", possible_paths[0]
  for next_possible_synset in indefinite_synsets[possible_paths[0][2]]:
    #print "with", next_possible_synset
    path_tuple_to_extend = possible_paths[0]
    current_distance = calculate_current_distance(next_possible_synset, path_tuple_to_extend[1], path_tuple_to_extend[0])
    current_path = copy_path(path_tuple_to_extend[1])
    current_path.append(next_possible_synset)
    bisect.insort(possible_paths, (current_distance, current_path, path_tuple_to_extend[2]+1))

  #remove extended path
  possible_paths.pop(0)
  #print "%d possible paths" % len(possible_paths)
  return possible_paths, False


def find_synsets_and_unmatched_tags(tag_list):
  indefinite_synsets = []
  synsets = []
  unmatched_tags = []

  for tag in tag_list:
    synsets_for_tag = wn.synsets(tag, pos=wn.NOUN)
    if len(synsets_for_tag) == 1:
      synsets.append(synsets_for_tag[0])
      #print "Eindeutiges Synset: " + str(synsets_for_tag[0])
    elif len(synsets_for_tag) > 1:
      indefinite_synsets.append(synsets_for_tag)
    elif len(synsets_for_tag) == 0:
      unmatched_tags.append(tag)

  # initialize possible paths with possible synsets for first undefined tag
  print len(indefinite_synsets), "synsets to find based on ", len(synsets)
  if len(indefinite_synsets) > 0:
    possible_paths = []
    for possible_synset in indefinite_synsets[0]:
      assumed_synsets = list(synsets)
      current_distance = calculate_current_distance(possible_synset, assumed_synsets, 0)
      assumed_synsets.append(possible_synset)
      bisect.insort(possible_paths, (current_distance, assumed_synsets, 1))
      #print possible_paths

    found_solution = False
    while not found_solution:
      possible_paths, found_solution = extend_best_path(possible_paths, indefinite_synsets)

    synsets.extend(possible_paths[0][1])

  #for indefinite_synset in indefinite_synsets:
    #initialize index to 0 so that if no tags with single synset (=synsets[index_of_json] empty), first synset will be chosen
    # max_sim_sum = (0, 0)
    # for index, synset in enumerate(indefinite_synset):
    #   sim_sum = 0
    #   for found_synset in synsets:
    #     sim_sum += synset.lch_similarity(found_synset)
    #   if sim_sum > max_sim_sum[0]:
    #     max_sim_sum = (sim_sum, index)
    # synsets.append(indefinite_synset[max_sim_sum[1]])
    #print "Ermitteltes Synset: ", (indefinite_synset[max_sim_sum[1]]), " (", indefinite_synset[max_sim_sum[1]].definition, ")"

  return synsets, unmatched_tags

def parse_json_data(json_files, number_of_jsons=10000):
  synsets_for_pictures = dict()
  for index_of_json, json_file in enumerate(json_files):
    if index_of_json > number_of_jsons:
      break
    tag_list, photo_data = read_data_from_json_file(json_file)
    if tag_list == None:
      continue

    synsets, unmatched_tags = find_synsets_and_unmatched_tags(tag_list)
    json_file = json_file[json_file.rfind(os.sep)+1:]
    synsets_for_pictures[json_file] = (photo_data["url"], synsets, unmatched_tags)
    print synsets_for_pictures[json_file]

  return synsets_for_pictures

def make_keywords_storable(keywords_for_pictures):
  storable_keywords_for_pictures = dict()
  for photo_filename, (photo_url, synsets, unmatched_tags) in keywords_for_pictures.iteritems():
    synset_names =[]
    for synset in synsets:
      synset_names.append(synset.name)
    storable_keywords_for_pictures[photo_filename] = (photo_url, synset_names, unmatched_tags)
  return storable_keywords_for_pictures

def restore_keywords_for_pictures(storable_keywords_for_pictures):
  keywords_for_pictures = dict()
  for photo_filename, (photo_url, synset_names, unmatched_tags) in storable_keywords_for_pictures.iteritems():
    synsets =[]
    for synset_name in synset_names:
      synsets.append(wn.synset(synset_name))
    keywords_for_pictures[photo_filename] = (photo_url, synsets, unmatched_tags)
  return keywords_for_pictures

def synset_detection(number_of_jsons=10000, subdirectory=None):
  # import configuration
  metadata_dir = import_metadata_dir_of_config('../config.cfg')

  if subdirectory == None:
    # read json files from metadata directory
    print_status("Reading %d Json Files... " % number_of_jsons)
    json_files = find_metajsons_to_process(metadata_dir)
    print "Done."
  else:
    metadata_dir += subdirectory
    json_files = find_metajsons_to_process_in_dir(metadata_dir)
    print "Using directory %s . %d files" % (metadata_dir, len(json_files))

  # parse data from json files
  print_status("Parsing json files and detecting synsets... ")
  keywords_for_pictures = parse_json_data(json_files,number_of_jsons)
  print "Done"

  # create a data structure where the names of synsets instead of synsets themself are stored
  print_status("Creating structure for writing to file... ")
  storable_keywords_for_pictures = make_keywords_storable(keywords_for_pictures)
  print "Done"

  # tag index dict saves the matching index of a tag in the laplace matrix
  print_status("Creating tag list... ")
  tag_list = tag_histogram.keys()
  print "Done."

  return keywords_for_pictures, storable_keywords_for_pictures

def parse_command_line_arguments():
  parser = argparse.ArgumentParser(description='ADD DESCRIPTION TEXT.')
  parser.add_argument('-d','--directory_to_preprocess', dest='directory_to_preprocess', type=str,
                      help='Specifies the directory which we want to preprocess')
  args = parser.parse_args()
  return args

def main(argv):
  arguments = parse_command_line_arguments()
  print "Calling synset detection for dir", arguments.directory_to_preprocess
  synset_detection(subdirectory=arguments.directory_to_preprocess)

if __name__ == '__main__':
    main(sys.argv[1:])

