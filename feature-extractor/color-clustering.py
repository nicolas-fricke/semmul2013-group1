#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# Script crawls images from flickr and parses them in SimpleCV
#
#
# Specify the metadata folder in the config file: ../config.cfg
#
# Use config.cfg.template as template for this file
#
#
# author: nicolas fricke
# mail: nicolas.fricke@student.hpi.uni-potsdam.de
################################################################################

import argparse
import ConfigParser
import json
import numpy as np
from collections import defaultdict
from SimpleCV import Image
from math import sqrt
from scipy.cluster.hierarchy import fclusterdata as hierarchial_cluster
# Import own module helpers
import sys
sys.path.append('../helpers')
from general_helpers import *
from visual_helpers import *

def distance_function(u, v):
  sum = 0
  for i in range(0, len(u)):
    #if i < 
    sum += (u[i] - v[i]) ** 2
  #sum_u = sum(u[20:30])
  #sum_v = sum(v[20:30])
  #diff  = abs(sum_u - sum_v)
  #print "distance: " + str(sqrt(sum))
  return sqrt(sum)

def tag_is_present(tag_content, tag_list):
  for tag in tag_list:
    if tag["_content"] == tag_content:
      return True
  return False

def main(argv):
  parser = argparse.ArgumentParser(description='ADD DESCRIPTION TEXT.')
  parser.add_argument('-p','--preprocessed', dest='use_preprocessed_data', action='store_true',
                   help='If specified, use preprocessed image data, otherwise download and process images and save values to file for next use')
  args = parser.parse_args()

  print_status("Use prerpocessed data: " + str(args.use_preprocessed_data) + "\n\n")

  if not args.use_preprocessed_data:
    # import configuration
    config = ConfigParser.SafeConfigParser()
    config.read('../config.cfg')

    api_key = config.get('Flickr API Key', 'key')
    metadata_dir = '../' + config.get('Directories', 'metadata-dir')

    metajson_files = find_metajsons_to_process(metadata_dir)

    print_status("Reading metadata files, loading images and calculating color histograms.... ")
    images = []
    file_number = 0
    for metajson_file in metajson_files:
      metadata = parse_json_file(metajson_file)
      if metadata["stat"] == "ok":
        if not tag_is_present("car", metadata["metadata"]["info"]["tags"]["tag"]):
          continue
        data = {}
        url      = get_small_image_url(metadata)
        data["image_id"]  = metadata["id"]
        data["file_path"] = metajson_file
        data["url"]       = url
        try:
          image = Image(url).toHSV()
        except Exception:
          continue
        (value, saturation, hue) = image.splitChannels()
        bins = zip(split_image_into_bins(hue, 9), split_image_into_bins(saturation.equalize(), 9), split_image_into_bins(value.equalize(), 9))
        data["colors"] = []
        for hue_bin, sat_bin, val_bin in bins:
          data["colors"] += hue_bin.histogram(20)
          data["colors"] += sat_bin.histogram(20)
          data["colors"] += val_bin.histogram(20)
        images.append(data)
        file_number += 1
      if file_number >= 100:
        break
    print "Done."
    save_object(images, "color_features.pickle")
  else:
    images = load_object("color_features.pickle")

  print_status("Building data structure for clustering.... ")
  colors = []
  for image_data in images:
    colors.append(image_data["colors"])
  print "Done."

  print_status("Clustering images by color histograms hierarchial_cluster algorithm with our own distance function.... ")
  clustered_images = hierarchial_cluster(colors, 0.71, criterion='inconsistent', metric='euclidean')#distance_function)
  #clustered_images = Pycluster.kcluster(colors, 8)
  print "Done."

  clusters = defaultdict(list)
  for index, cluster in enumerate(clustered_images):
    clusters[cluster].append(images[index])

  write_clusters_to_html(clusters, open_in_browser=True)

if __name__ == '__main__':
    main(sys.argv[1:])