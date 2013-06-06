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
import nltk
from nltk.corpus import wordnet as wn
import re # Regex
import string
import operator
from math import log

# Import own modules
import sys
sys.path.append('../helpers')
from general_helpers import *

# Global variables
tag_histogram = Counter()
tag_co_occurrence_histogram = Counter()


################     Reading of Files       ####################################

# probably add preprocessing steps for tags
def read_tags_from_json(json_data):
  tag_list = []
  for raw_tag in json_data["metadata"]["info"]["tags"]["tag"]:
    # Preprocess tag before appending to tag_list
    tag = raw_tag["raw"]
    tag_array = string.split(tag," ")      # split by space
    for tag in tag_array:
      tag = re.sub("[0-9]","", tag)        # cut off digits
      tag = string.lower(tag)              # Only lower case
      tag = wn.morphy(tag)                 # Stemmming
      if not tag == None and len(tag) > 2: # Only tags with more than 2 literals
        tag_list.append(str(tag))
  return tag_list

def read_data_from_json_file(json_file):
  f = open(json_file)
  json_data = json.load(f)
  f.close()
  data = {}   # Create data dict for image visualization
  if json_data["stat"] == "ok":
    data["image_id"]  = json_data["id"]
    data["url"] = get_small_image_url(json_data)
    return read_tags_from_json(json_data), data
  return None, None

def import_metadata_dir_of_config(path):
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  return '../' + config.get('Directories', 'metadata-dir')

def parse_json_data(json_files,number_of_jsons):
  tag_histogram = Counter()
  tag_co_occurrence_histogram = Counter()
  photo_tags_dict = {}
  photo_data_list = {}
  for count,json_file in enumerate(json_files):
    if count > number_of_jsons:
      break
    tag_list, photo_data = read_data_from_json_file(json_file)
    if not photo_data == None:
      photo_tags_dict[int(photo_data["image_id"])] = tag_list
      photo_data_list[int(photo_data["image_id"])] = photo_data
    if not tag_list == None:
      tag_histogram.update(tag_list)
      tag_co_occurrence_histogram.update([(tag1,tag2) for tag1 in tag_list for tag2 in tag_list if tag1 < tag2])
  return tag_histogram, tag_co_occurrence_histogram, photo_tags_dict, photo_data_list

def remove_tags_with_small_occurence(cut_off_percentage):
  new_tag_histogram = {}
  cut_off_threshold = (len(tag_histogram) * cut_off_percentage)/100
  sorted_tag_histogram = sorted(tag_histogram.iteritems(), key=operator.itemgetter(1))
  for (key, val) in sorted_tag_histogram:
    if cut_off_threshold > 0:
      cut_off_threshold -= 1
      continue
    else:
      new_tag_histogram[key] = val
  new_tag_co_occurence_histogram = {}
  for (key1,key2),val in tag_co_occurrence_histogram.items():
    if new_tag_histogram.get(key1) and new_tag_histogram.get(key2):
      new_tag_co_occurence_histogram[(key1,key2)] = val
  return  new_tag_histogram, new_tag_co_occurence_histogram


################     Tag Clustering       ####################################

def create_tag_index_dict(tag_histogram):
  tag_dict = dict()
  for index, tag in enumerate(tag_histogram.keys()):
    tag_dict[tag] = index
  return tag_dict


################     Tag Preprocessing      ####################################

def tag_preprocessing(number_of_jsons):
  # import configuration
  metadata_dir = import_metadata_dir_of_config('../config.cfg')

  # read json files from metadata directory
  print_status("Reading %d Json Files... " % number_of_jsons)
  json_files = find_metajsons_to_process(metadata_dir)
  print "Done."

  # parse data from json files
  global tag_histogram
  global tag_co_occurrence_histogram
  print_status("Parsing json files, creating histograms and tags dictionary... ")
  tag_histogram, tag_co_occurrence_histogram, photo_tags_dict, photo_data_list = parse_json_data(json_files,number_of_jsons)
  print "Done, with %2d Tags" % len(tag_histogram)
  #print photo_tags_dict

  # remove X percent tags with too small occurence from the histograms
  cut_off_percentage = 10
  print_status("Removing the lower %d%% of tags from histograms... " % cut_off_percentage)
  tag_histogram, tag_co_occurrence_histogram = remove_tags_with_small_occurence(cut_off_percentage)
  print "Done, %2d Tags remaining" % len(tag_histogram)

  # remove tags with too small and too high Tf-idf value (occure too seldom or too often)
  # sorted_tag_histogram = sorted(tag_histogram.iteritems(), key=operator.itemgetter(1))
  # print "Tag \t Frequency \t Tf-idf"
  # (_,highest_val) = sorted_tag_histogram[-1]
  # for (key, val) in sorted_tag_histogram:
  #   tf_idf = 0
  #   for photo_taglist in photo_tags_dict.values():
  #     if key in photo_taglist:
  #       tf_idf += log(number_of_jsons/float(val)) # * freq(val) / freq(highest_val)
  #   print "%s \t %d \t %f" % (key,val,tf_idf)

  # tag index dict saves the matching index of a tag in the laplace matrix
  print_status("Creating tag dictionary... ")
  tag_index_dict = create_tag_index_dict(tag_histogram)
  print "Done."
  #print tag_index_dict

  return tag_co_occurrence_histogram, tag_index_dict, photo_tags_dict, photo_data_list
