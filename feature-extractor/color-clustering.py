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
from collections import defaultdict
from SimpleCV import Image
from Pycluster import kcluster
# Import own module helpers
import sys
sys.path.append('../helpers')
from general_helpers import *
from visual_helpers import *

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
        data = {}
        url      = get_small_image_url(metadata)
        data["image_id"]  = metadata["id"]
        data["file_path"] = metajson_file
        data["url"]       = url
        try:
          image = Image(url).toHSV()
        except Exception:
          continue
        bins = split_image_into_bins(image, 16)
        data["colors"] = []
        for bin in bins:
          (value, saturation, hue) = bin.splitChannels()
          data["colors"] += hue.histogram(20)
          data["colors"] += saturation.histogram(20)
          data["colors"] += value.histogram(20)
        images.append(data)
        file_number += 1
      if file_number >= 400:
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

  print_status("Clustering images by color histograms via k-means algorithm.... ")
  clustered_images, value, _ = kcluster(colors, 20)
  print "Done."

  clusters = defaultdict(list)
  for index, cluster in enumerate(clustered_images):
    clusters[cluster].append(images[index])

  write_clusters_to_html(clusters, open_in_browser=True)

if __name__ == '__main__':
    main(sys.argv[1:])