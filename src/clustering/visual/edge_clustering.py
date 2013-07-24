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

import ConfigParser
import json
import os.path
from collections import defaultdict
from SimpleCV import Image
from SimpleCV import EdgeHistogramFeatureExtractor
from Pycluster import kcluster
# Import own module helpers
import sys
from helpers.general_helpers import *
from helpers.visual_helpers import *

def extract_edges(image, data, slices):
  edgeExtractor = EdgeHistogramFeatureExtractor(bins=4)
  image_bins = split_image_into_slices(image, slices)
  data["edge-angles"]  = []
  data["edge-lengths"] = []
  for image_bin in image_bins:
    edge_angles_and_lengths = edgeExtractor.extract(image_bin)
    data["edge-angles"]  += edge_angles_and_lengths[:len(edge_angles_and_lengths) / 2]
    data["edge-lengths"] += edge_angles_and_lengths[len(edge_angles_and_lengths) / 2:]
  return data

def main():
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')

  api_key = config.get('Flickr API Key', 'key')
  metadata_dir = '../' + config.get('Directories', 'metadata-dir')

  metajson_files = find_metajsons_to_process(metadata_dir)

  print_status("Reading metadata files, loading images and calculating edge histograms.... ")
  images = []
  for file_number, metajson_file in enumerate(metajson_files):
    metadata = parse_json_file(metajson_file)
    if metadata == None:
      print "Could not read json file %s" % metajson_file
      continue

    if metadata["stat"] == "ok":
      data = {}
      url      = get_small_image_url(metadata)
      data["image_id"]  = metadata["id"]
      data["file_name"] = metajson_file.split(os.sep)[-1]
      data["url"]       = url
      try:
        image = Image(url)
      except Exception:
        continue
      images.append(extract_edges(image, data, 4))
    if file_number > 50:
      break
  print "Done."

  print_status("Building data structure for clustering.... ")
  edges = []
  for image_data in images:
    edges.append(image_data["edge-angles"] + image_data["edge-lengths"])
  print "Done."

  print_status("Clustering images by edge histograms via k-means algorithm.... ")
  clustered_images, value, _ = kcluster(edges, 10)
  print "Done."

  clusters = defaultdict(list)
  for index, cluster in enumerate(clustered_images):
    clusters[cluster].append(images[index])

  write_clusters_to_html(clusters, open_in_browser=True)

if __name__ == '__main__':
    main()
