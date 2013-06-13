import ConfigParser
import json
from nltk.corpus import wordnet as wn
import re # Regex
import string
import operator

# Import own modules
import sys
sys.path.append('../helpers')
from general_helpers import *
from tag_preprocessing import *


def parse_json_data(json_files, number_of_jsons):
  synsets = {}
  for count,json_file in enumerate(json_files):
    if count > number_of_jsons:
      break
    synsets[count] = []
    tag_list, photo_data = read_data_from_json_file(json_file)
    synset_lists = []
    if tag_list == None:
      continue
    print "############ ", photo_data["url"], " ##########"
    for tag in tag_list:
      synsets_for_tag = wn.synsets(tag, pos=wn.NOUN)
      if len(synsets_for_tag) == 1:
        synsets[count].append(synsets_for_tag[0])
        print "Eindeutiges Synset: " + str(synsets_for_tag[0])
      elif len(synsets_for_tag) > 1:
        synset_lists.append(synsets_for_tag)

    for synset_list in synset_lists:
      #initialize index to 0 so that if no tags with single synset (=synsetes[count] empty), first synset will be chosen
      max_sim_sum = (0, 0)
      for index, synset in enumerate(synset_list):
        sim_sum = 0
        for found_synset in synsets[count]:
          sim_sum += synset.lch_similarity(found_synset)
        if sim_sum > max_sim_sum[0]:
          max_sim_sum = (sim_sum, index)
      synsets[count].append(synset_list[max_sim_sum[1]])
      print "Ermitteltes Synset: ", (synset_list[max_sim_sum[1]]), " (", synset_list[max_sim_sum[1]].definition, ")"

      

def synset_detection(number_of_jsons):
  # import configuration
  metadata_dir = import_metadata_dir_of_config('../config.cfg')

  # read json files from metadata directory
  print_status("Reading %d Json Files... " % number_of_jsons)
  json_files = find_metajsons_to_process(metadata_dir)
  print "Done."

  # parse data from json files
  print_status("Parsing json files, creating histograms and tags dictionary... ")
  parse_json_data(json_files,number_of_jsons)
  print "Done, with %2d Tags" % len(tag_histogram)

  # tag index dict saves the matching index of a tag in the laplace matrix
  print_status("Creating tag list... ")
  tag_list = tag_histogram.keys()
  print "Done."

  return None

def main():
  synset_detection(100)

if __name__ == '__main__':
    main()