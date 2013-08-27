#!/usr/bin/python
# -*- coding: utf-8 -*-

######################################################################################
#
# Preprocess all the given pictures' visual features and write them into the 
#  pictures' json-file
#
# usage: python preprocess_visual_features.py
#               --directory_to_preprocess <directory which should be preprocessed>
#               --read_images_from_disk <if set, read images from directory instead of redownload from flickr>
#
# authors: Mandy Roick
# mail: mandy.roick@student.hpi.uni-potsdam.de
######################################################################################

import argparse
import ConfigParser
import os.path
import sys
from SimpleCV import Image

# Import own module helpers
from helpers.general_helpers import *
from clustering.visual.color_clustering import extract_colors
from clustering.visual.edge_clustering import extract_edges

def preprocess_visual_features_for_jsons(metajson_files, downloaded_images_dir=None):
  for metajson_file in metajson_files:

    metadata = parse_json_file(metajson_file)
    if metadata == None:
      print "Could not read json file %s" % metajson_file
      continue

    print_status("ID: " + metadata["id"] + " File name: " + metajson_file + "\n")
    if metadata["stat"] == "ok":
      try:
        if not downloaded_images_dir == None:
          image_filename = metajson_file.split(os.sep)[-1].replace('.json', '.jpg')
          image_path = downloaded_images_dir + os.sep + image_filename
          image = Image(image_path).toHSV()
        else:
          url = get_small_image_url(metadata)
          image = Image(url).toHSV()
      except Exception:
        print "Could not get image:", metadata["id"]
        continue

      visual_data = {}
      visual_data = extract_colors(image, visual_data, 5)
      visual_data = extract_edges(image, visual_data, 5)

      file_name_for_visual_metadata = metajson_file.replace('.json', '_visual.json')
      write_json_file(visual_data, file_name_for_visual_metadata)

    else:
      print "Status was not ok:", metadata["id"]


def parse_command_line_arguments():
  parser = argparse.ArgumentParser(description='ADD DESCRIPTION TEXT.')
  parser.add_argument('-d','--directory_to_preprocess', dest='directory_to_preprocess', type=str,
                      help='Specifies the directory in metadata-dir which we want to preprocess')
  parser.add_argument('-r','--read_images_from_disk', dest='read_images_from_disk', action='store_true',
                      help='Specifies whether image files should be read from disk rather than downloaded from flickr, specify image path in config file')
  args = parser.parse_args()
  return args

def main(argv):
  arguments = parse_command_line_arguments()

  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')

  metadata_dir = config.get('Directories', 'metadata-dir')
  if arguments.read_images_from_disk:
    downloaded_images_dir = config.get('Directories', 'downloaded-images-dir')
  else: 
    downloaded_images_dir = None

  # read metajsons
  if arguments.directory_to_preprocess:
    metajsons_full_path = metadata_dir + arguments.directory_to_preprocess
    metajson_files = find_metajsons_to_process_in_dir(metajsons_full_path)
  else:
    metajson_files = find_metajsons_to_process(metadata_dir)

  # preprocess visual features and write them to file
  print_status("Reading metadata files, loading images and calculating color and edge histograms.... \n")
  preprocess_visual_features_for_jsons(metajson_files, downloaded_images_dir)
  print "Done."

if __name__ == '__main__':
    main(sys.argv[1:])