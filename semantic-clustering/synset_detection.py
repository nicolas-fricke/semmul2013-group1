import ConfigParser
import json
from nltk.corpus import wordnet as wn
from collections import defaultdict
import operator

# Import own modules
import sys
sys.path.append('../helpers')
from general_helpers import *
from tag_preprocessing import *


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

  for indefinite_synset in indefinite_synsets:
    #initialize index to 0 so that if no tags with single synset (=synsets[index_of_json] empty), first synset will be chosen
    max_sim_sum = (0, 0)
    for index, synset in enumerate(indefinite_synset):
      sim_sum = 0
      for found_synset in synsets:
        sim_sum += synset.lch_similarity(found_synset)
      if sim_sum > max_sim_sum[0]:
        max_sim_sum = (sim_sum, index)
    synsets.append(indefinite_synset[max_sim_sum[1]])
    #print "Ermitteltes Synset: ", (indefinite_synset[max_sim_sum[1]]), " (", indefinite_synset[max_sim_sum[1]].definition, ")"

  return synsets, unmatched_tags

def parse_json_data(json_files, number_of_jsons):
  synsets_for_pictures = dict()
  for index_of_json, json_file in enumerate(json_files):
    if index_of_json > number_of_jsons:
      break
    tag_list, photo_data = read_data_from_json_file(json_file)
    if tag_list == None:
      continue

    synsets, unmatched_tags = find_synsets_and_unmatched_tags(tag_list)
    json_file = json_file[json_file.rfind("/")+1:]
    synsets_for_pictures[json_file] = (photo_data["url"], synsets, unmatched_tags)

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

def synset_detection(number_of_jsons):
  # import configuration
  metadata_dir = import_metadata_dir_of_config('../config.cfg')

  # read json files from metadata directory
  print_status("Reading %d Json Files... " % number_of_jsons)
  json_files = find_metajsons_to_process(metadata_dir)
  print "Done."

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