#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# Preprocesses the tags from the metadata crawling
#
# config file: ../config.cfg
#
# Use config.cfg.template as template for this file
#
#
# author: tino junge
# mail: tino.junge@student.hpi.uni-potsdam.de
################################################################################

import ConfigParser
from collections import Counter
import json
import glob
from pprint import pprint

def read_tags_from_json(json_data):
  tag_list = []
  for tag in json_data["metadata"]["info"]["tags"]["tag"]:
    tag_list.append(tag["raw"])
  return tag_list

def get_json_files(metadata_dir):
  return glob.glob(metadata_dir + '/*/*/*.json')

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

  # get tags and count them
  counter = Counter()
  for json_file in json_files:
    tag_list = read_tags_from_file(json_file)
    if not tag_list == None:
      counter.update(tag_list)
  print counter

if __name__ == '__main__':
    main()
