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


def parse_json_data(json_files, number_of_jsons):
  synsets_for_pictures = defaultdict(list)
  for index_of_json, json_file in enumerate(json_files):
    if index_of_json > number_of_jsons:
      break
    tag_list, photo_data = read_data_from_json_file(json_file)
    if tag_list == None:
      continue
    print "############ ", photo_data["url"], " ##########"

    synsets_for_pictures[photo_data["url"]] = []
    indefinite_synsets = []

    for tag in tag_list:
      synsets_for_tag = wn.synsets(tag, pos=wn.NOUN)
      if len(synsets_for_tag) == 1:
        synsets_for_pictures[photo_data["url"]].append(synsets_for_tag[0])
        print "Eindeutiges Synset: " + str(synsets_for_tag[0])
      elif len(synsets_for_tag) > 1:
        indefinite_synsets.append(synsets_for_tag)

    for indefinite_synset in indefinite_synsets:
      #initialize index to 0 so that if no tags with single synset (=synsetes[index_of_json] empty), first synset will be chosen
      max_sim_sum = (0, 0)
      for index, synset in enumerate(indefinite_synset):
        sim_sum = 0
        for found_synset in synsets_for_pictures[photo_data["url"]]:
          sim_sum += synset.lch_similarity(found_synset)
        if sim_sum > max_sim_sum[0]:
          max_sim_sum = (sim_sum, index)
      synsets_for_pictures[photo_data["url"]].append(indefinite_synset[max_sim_sum[1]])
      print "Ermitteltes Synset: ", (indefinite_synset[max_sim_sum[1]]), " (", indefinite_synset[max_sim_sum[1]].definition, ")"
  return synsets_for_pictures

def synset_detection(number_of_jsons):
  # import configuration
  metadata_dir = import_metadata_dir_of_config('../config.cfg')

  # read json files from metadata directory
  print_status("Reading %d Json Files... " % number_of_jsons)
  json_files = find_metajsons_to_process(metadata_dir)
  print "Done."

  # parse data from json files
  print_status("Parsing json files, creating histograms and tags dictionary... ")
  keywords_for_pictures = parse_json_data(json_files,number_of_jsons)
  print "Done, with %2d Tags" % len(tag_histogram)

  print_status("Write preprocessed data to file ...")
  save_object(keywords_for_pictures, "preprocessed_data")
  print "Done"

  # tag index dict saves the matching index of a tag in the laplace matrix
  print_status("Creating tag list... ")
  tag_list = tag_histogram.keys()
  print "Done."

  return None