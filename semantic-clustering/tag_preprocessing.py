#!/usr/bin/python
# -*- coding: utf-8 -*-

######################################################################################
# Preprocesses the tags from the metadata crawling
#
# config file: ../config.cfg
#
# Use config.cfg.template as template for this file
#
#
# authors: tino junge, mandy roick
# mail: tino.junge@student.hpi.uni-potsdam.de, mandy.roick@student.hpi.uni-potsdam.de
######################################################################################

import ConfigParser
from collections import Counter
import json
import glob
from pprint import pprint
import nltk
from nltk.corpus import wordnet as wn
import numpy as np

def read_tags_from_json(json_data):
  tag_list = []
  for raw_tag in json_data["metadata"]["info"]["tags"]["tag"]:
    # Preprocess tag before appending to tag_list
    tag = raw_tag["_content"]
    #tag = tag.lower               # Only lower case
    #tag = wn.morphy(tag)          # Stemmming
    tag_list.append(tag)
  return tag_list

def get_json_files(metadata_dir):
  return glob.glob(metadata_dir + '/*/*/1000*.json')

def read_tags_from_file(json_file):
  f = open(json_file)
  json_data = json.load(f)
  f.close()
  tag_list = []
  if json_data["stat"] == "ok":
    return read_tags_from_json(json_data)
  return None

def main():
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  metadata_dir = '../' + config.get('Directories', 'metadata-dir')

  # read json files from metadata directory
  json_files = get_json_files(metadata_dir)
  print "Done Reading " + str(len(json_files)) + " Json Files"

  # get list of all tags and count there co-occurrences
  tag_histogram = Counter()
  tag_co_occurrence_histogram = Counter()
  for json_file in json_files:
    tag_list = read_tags_from_file(json_file)
    if not tag_list == None:
      tag_histogram.update(tag_list)
      tag_co_occurrence_histogram.update([(tag1,tag2) for tag1 in tag_list for tag2 in tag_list if tag1 < tag2])
  #print tag_histogram
  #print tag_co_occurrence_histogram
  print "Done histogram creation. %2d Tags" % len(tag_histogram)

  # initialize tag dictionary
  tag_dict = dict()
  for i, key in enumerate(tag_histogram.keys()):
    tag_dict[key] = i
  print "Done Tag Dict"
  print tag_dict

  # create laplace matrice
  laplace_matrice = np.zeros((len(tag_histogram),len(tag_histogram)))
  for (tag1, tag2) in tag_co_occurrence_histogram:
    laplace_matrice[tag_dict[tag1]][tag_dict[tag2]] = -1
    laplace_matrice[tag_dict[tag2]][tag_dict[tag1]] = -1

  np.set_printoptions(threshold='nan')
  print  laplace_matrice

if __name__ == '__main__':
    main()
