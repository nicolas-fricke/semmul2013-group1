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

def find_hyponyms_on_wordnet(word):
  hyponyms_lists = []
  for synset in wn.synsets(word):
    hyponym_list = []
    for hyponym in synset.hyponyms():
      hyponym_list.append(hyponym.name)

    hyponyms_lists.append(hyponym_list)
  return hyponyms_lists

def search_photos_for_hyponyms(hyponyms, photo_tags_dict):
  synonyms_photo_lists = []
  for hyponym_name in hyponyms:
    synonym_photo_list = []
    for photo_id, tag_list in photo_tags_dict.items():
      if hyponym_name in tag_list: # or (hyponym_name in tag_list and synonym_name in tag_list)
        synonym_photo_list.append(photo_id)
    synonyms_photo_lists.append(synonym_photo_list)
  return synonyms_photo_lists

def main(argv):
  ####### Reading Commandline arguments ########
  word, number_of_jsons = parse_command_line_arguments(argv)

  ####### Getting Tag List ######

  print_status("Running tag_preprocessing for %d Jsons...\n" % number_of_jsons)
  tag_co_occurrence_histogram, tag_index_dict, tag_similarity_histogram, photo_tags_dict, photo_data_list = tag_preprocessing(number_of_jsons)
  print_status("Finishing tag_preprocessing.\n")

  ####### WordNet Search #######

  print_status("Running WordNet Search for %s..." % word)
  hyponyms_lists = find_hyponyms_on_wordnet(word)
  print "Done."

  print hyponyms_lists


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
  # print_status("Done.\n")


if __name__ == '__main__':
  main(sys.argv[1:])
