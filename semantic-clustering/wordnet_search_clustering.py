#!/usr/bin/python
# -*- coding: utf-8 -*-

######################################################################################
#
# Search the given word in wordnet and try to cluster images which belongs to it
#
#
# authors: tino junge, nicolas fricke
# mail: {tino.junge nicolas.fricke}@student.hpi.uni-potsdam.de
######################################################################################

import sys
import getopt
from nltk.corpus import wordnet as wn
from collections import defaultdict


# Import own modules
sys.path.append('../helpers')
from general_helpers import *
from tag_preprocessing import *

def get_synset_name(synset):
  return synset.name.split(".")[0]


def parse_command_line_arguments(argv):
  ####### Reading Commandline arguments ########

  word = ''
  number_of_jsons = 0
  try:
    opts, args = getopt.getopt(argv,"n:w:",["number_of_jsons=","word="])
  except getopt.GetoptError:
    print 'wordnet_search_clustering.py -n <number_of_jsons> -w <word>'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-n':
      number_of_jsons = int(arg)
    elif opt == '-w':
      word = arg
    else:
      print 'wordnet_search_clustering.py -n <number_of_jsons> -w <word>'
      sys.exit()

  if word == '':
    print 'Error1: parameter word cannot be blank'
    print 'Syntax: wordnet_search_clustering.py -n <number_of_jsons> -w <word>'
    sys.exit()
  if number_of_jsons == 0:
    print 'Error2: parameter number_of_jsons cannot be zero'
    print 'Syntax: wordnet_search_clustering.py -n <number_of_jsons> -w <word>'
    sys.exit()

  return word, number_of_jsons

def recursively_find_all_hyponyms_on_wordnet(synset_name):
  synset = wn.synset(synset_name)
  hyponyms = synset.hyponyms()
  if len(hyponyms) == 0:
    return None
  else:
    hyponyms_of_synset = {}
    for hyponym in hyponyms:
      hyponyms_of_synset[hyponym.name] = recursively_find_all_hyponyms_on_wordnet(hyponym.name)
    return hyponyms_of_synset

def find_hyponyms_on_wordnet(word):
  hyponym_tree = {}
  for synset in wn.synsets(word):
    hyponym_tree[synset.name] = recursively_find_all_hyponyms_on_wordnet(synset.name)
  return hyponym_tree

def search_photos_for_hyponyms(hyponyms, photo_tags_dict):
  synonyms_photo_lists = []
  for hyponym_name in hyponyms:
    synonym_photo_list = []
    for photo_id, tag_list in photo_tags_dict.items():
      if hyponym_name in tag_list: # or (hyponym_name in tag_list and synonym_name in tag_list)
        synonym_photo_list.append(photo_id)
    synonyms_photo_lists.append(synonym_photo_list)
  return synonyms_photo_lists

def build_inverted_tag_index(photo_tags_dict):
  inverted_tag_index = defaultdict(list)
  for photo_id, photo_tags in photo_tags_dict.items():
    for tag in photo_tags:
      inverted_tag_index[tag].append(photo_id)
  return inverted_tag_index

def add_photos_to_hyponym_lists(hyponyms_lists,inverted_tag_index):
  if hyponyms_lists == None:
    return None
  else:
    for hyponym, hyponym_list in hyponyms_lists.items():
      hyponym_name = hyponym.split(".")[0]
      print hyponym_name
      print inverted_tag_index.get(hyponym_name)
      if inverted_tag_index.get(hyponym_name):
        print "Matching!!"
      if hyponym_list == None:
        return None
      else:
        for hyponym_dict in hyponym_list:
          add_photos_to_hyponym_lists(hyponym_dict,inverted_tag_index)
  return hyponyms_lists

def pretty_print_dict(d, indent=0):
   parent_indent = indent - 1 if indent > 0 else 0
   if not isinstance(d, dict): return
   for key, value in d.iteritems():
      print '|   ' * parent_indent + ('|-- ' if indent > 0 else "")  + str(key)
      if isinstance(value, dict):
         pretty_print_dict(value, indent + 1)

def count_nested_dict(d):
  counter = 0
  for value in d.values():
    counter += 1
    if value != None:
      counter += count_nested_dict(value)
  return counter

def main(argv):
  ####### Reading Commandline arguments ########
  word, number_of_jsons = parse_command_line_arguments(argv)


  # ####### Getting JSON files #########

  # # import configuration
  # metadata_dir = import_metadata_dir_of_config('../config.cfg')

  # print_status("Reading %d Json Files... " % number_of_jsons)
  # json_files = find_metajsons_to_process(metadata_dir)
  # print "Done."


  # ####### Getting Photo Tag List ######

  # print_status("Parsing photo_tags_dict for %d Jsons... " % number_of_jsons)
  # photo_tags_dict = parse_photo_tags_from_json_data(json_files,number_of_jsons,)
  # print "Done."

  ####### WordNet Search #######

  print_status("Running WordNet Search for %s... " % word)
  hyponyms_trees = find_hyponyms_on_wordnet(word)
  print "Done."

  pretty_print_dict(hyponyms_trees)

  # print_status("Building inverted_tag_index... ")
  # inverted_tag_index = build_inverted_tag_index(photo_tags_dict)
  # print "Done."

  # print_status("Check if photo_tags in hyponyms_lists... ")
  # hyponyms_lists = add_photos_to_hyponym_lists(hyponyms_lists,inverted_tag_index)
  # print "Done."

  # TODO: 1) recursively iterate over hyponyms and check in inverted index which photos have this tag
  #       2) visualize image clusters, make one cluster per hyponym with all subimages as subclusters

  # ####### Write clusters to html ######

  # print_status("Writing Clusters...")
  # clusters = defaultdict(list)
  # additional_columns= {}
  # additional_columns["hyponyms"] = []
  # for index, photo_list in enumerate(synonyms_photo_lists):
  #   additional_columns["hyponyms"].append(hyponyms_lists[index])
  #   for photo_id in photo_list:
  #     clusters[index].append(dict(photo_data_list[photo_id].items()))

  # name_of_html_file = str(number_of_jsons) + "_wordnet_search_clustering.html"
  # write_clusters_to_html(clusters, html_file_path=name_of_html_file, additional_columns=additional_columns, open_in_browser=True)
  # print "Done."
  print_status("Done. Found %d entries.\n" % count_nested_dict(hyponyms_trees))


if __name__ == '__main__':
  main(sys.argv[1:])
