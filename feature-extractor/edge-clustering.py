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
import sys
import time
import json
import glob
from collections import defaultdict
from SimpleCV import Image
from SimpleCV import EdgeHistogramFeatureExtractor
from Pycluster import kcluster

def print_status(message):
  sys.stdout.write(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + " - ")
  sys.stdout.write(message)
  sys.stdout.flush()

def find_metajsons_to_process(metadata_path):
  return glob.glob(metadata_path + '/*/*/*.json')

def parse_json_file(json_file):
  with open(json_file) as file:
    return json.load(file)

def get_small_image_url(metajson):
  if not metajson.get("stat") == "ok":
    return None
  sizes = metajson["metadata"]["sizes"]
  if not sizes.get("stat") == "ok":
    return None
  return [entry["source"] for entry in sizes["sizes"]["size"] if entry["label"] == "Small"][0]

def write_clusters_to_html(clusters, html_file="out.html"):
  output_html =  ( "<html>"
                   "  <head>"
                   "    <title>Cluster Visualization</title>"
                   "  </head>"
                   "  <body>"
                   "    <table border='1'>"
                   "      <tr><th>Cluster</th><th>Images</th></tr>")
  for cluster_number, images in clusters.iteritems():
    output_html += "      <tr><td>%d</td><td>" % cluster_number
    for image in images:
      output_html += "        <img src='%s' />" % image["url"]
    output_html += "      </td></tr>"
  output_html += ( "    </table>"
                   "  </body>"
                   "</html>")
  with open(html_file, "w") as output_file:
    output_file.write(output_html)

def main():
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')

  api_key = config.get('Flickr API Key', 'key')
  metadata_dir = '../' + config.get('Directories', 'metadata-dir')

  metajson_files = find_metajsons_to_process(metadata_dir)

  print_status("Reading metadata files, loading images and calculating edge histograms.... ")
  edgeExtractor = EdgeHistogramFeatureExtractor()
  images = []
  for file_number, metajson_file in enumerate(metajson_files):
    metadata = parse_json_file(metajson_file)
    if metadata["stat"] == "ok":
      data = {}
      url      = get_small_image_url(metadata)
      data["image_id"]  = metadata["id"]
      data["file_path"] = metajson_file
      data["url"]       = url
      try:
        image = Image(url)
      except Exception:
        continue
      data["edges"]     = edgeExtractor.extract(image)
      images.append(data)
    if file_number > 100:
      break
  print "Done."

  print_status("Building data structure for clustering.... ")
  edges = []
  for image_data in images:
    edges.append(image_data["edges"])
  print "Done."

  print_status("Clustering images by edge histograms via k-means algorithm.... ")
  clustered_images, value, _ = kcluster(edges, 20)
  print "Done."

  clusters = defaultdict(list)
  for index, cluster in enumerate(clustered_images):
    clusters[cluster].append(images[index])

  write_clusters_to_html(clusters)

if __name__ == '__main__':
    main()
