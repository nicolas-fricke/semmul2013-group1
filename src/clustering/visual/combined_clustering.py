import argparse
import ConfigParser
import json
import numpy as np
import os.path
import math
from collections import defaultdict
from SimpleCV import Image
from math import log, pow
from scipy.cluster.hierarchy import fclusterdata as hierarchial_cluster
from Pycluster import kcluster
from json import dumps

# Import own module helpers
from helpers.general_helpers import *
from helpers.visual_helpers import *
from clustering.visual.color_clustering import extract_colors
from clustering.visual.edge_clustering import extract_edges

# Extracting features (live)
def extract_features(image_cluster, metadata_dir):
  images = []
  for metajson_file, _ in image_cluster:
    relative_path_to_json = construct_path_to_json(metajson_file)
    full_path_to_json = metadata_dir + relative_path_to_json
    metadata = parse_json_file(full_path_to_json)
    if metadata == None:
      continue
    if metadata["stat"] == "ok":
      data = {}
      url = get_small_image_url(metadata)
      data["image_id"]  = metadata["id"]
      data["file_path"] = metajson_file
      data["url"]       = url
      try:
        image = Image(url).toHSV()
      except Exception:
        continue

      data = extract_colors(image, data, 5)
      data = extract_edges(image, data, 5)
      images.append(data)
  return images

# Reading preprocessed visual features from file
def read_features_from_file(cluster, features_json_filename, metadata_dir):
  images = []
  features_json_file = parse_json_file(features_json_filename)
  if features_json_file == None:
    return images
  for picture_json_filename, _ in cluster:
    relative_path_to_json = construct_path_to_json(picture_json_filename)
    full_path_to_json = metadata_dir + relative_path_to_json
    picture_json_file = parse_json_file(full_path_to_json)
    if picture_json_file == None:
      continue

    if picture_json_file["stat"] == "ok":
      try:
        data = features_json_file[picture_json_file["id"]]
        data["image_id"] = picture_json_file["id"]
        images.append(data)
      except KeyError:
        continue

  return images

# Holding visual features in memory
def assign_visual_features(cluster, visual_features, metadata_dir):
  images = []
  for picture_json_filename, _ in cluster:
    relative_path_to_json = construct_path_to_json(picture_json_filename)
    full_path_to_json = metadata_dir + relative_path_to_json
    picture_json_file = parse_json_file(full_path_to_json)
    if picture_json_file == None:
      continue

    if picture_json_file["stat"] == "ok":
      try:
        data = visual_features[picture_json_file["id"]]
        data["image_id"] = picture_json_file["id"]
        images.append(data)
      except KeyError:
        continue

  return images


def cluster_by_single_feature(feature_matrix):
  k = int(math.floor(math.sqrt(len(feature_matrix)/2.0)))
  clustered_images_by_color, _, _ = kcluster(feature_matrix, k, npass=5)   
  return clustered_images_by_color, k


def cluster_by_edges(edges):
  k_edges = 2
  clustered_images_by_edges, error, _ = kcluster(edges, k_edges, npass=5)
  previous_error = error * 10
  while 1/log(k_edges+0.0000001)*error > 1/log(k_edges-0.999999)*previous_error and k_edges < len(edges):
  #while error < 0.85 * previous_error:
    k_edges += 1
    previous_error = error
    clustered_images_by_edges, error, _ = kcluster(edges, k_edges, npass=5)
  k_edges -= 1
  clustered_images_by_edges, error, nfound = kcluster(edges, k_edges, npass=10)

  return clustered_images_by_edges, k_edges


def cluster_by_features(images):
  colors = []
  edges = []

  for image_data in images:
    colors.append(image_data["colors"])
    edges.append(image_data["edge-angles"] + image_data["edge-lengths"])

  clustered_images_by_color, k_color = cluster_by_single_feature(colors)
  clustered_images_by_edges, k_edges = cluster_by_single_feature(edges)

  #DO LATE FUSION
  clusters = defaultdict(list)
  for index, cluster_color in enumerate(clustered_images_by_color):
    cluster_edges = clustered_images_by_edges[index]
    clusters[str(cluster_color + cluster_edges * k_color)].append((images[index]["file_path"], images[index]["url"]))
  return clusters


def cluster_visually(tree_node, visual_clustering_threshold=8, visual_features=None):
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  metadata_dir = config.get('Directories', 'metadata-dir')
  if visual_features == None:
    visual_features_filename = config.get('Filenames for Pickles', 'visual_features_filename')
    visual_features_filename = visual_features_filename.replace('##', 'all')

  new_subclusters = []
  for representatives_and_cluster_dict in tree_node.subclusters:
    cluster = representatives_and_cluster_dict["subcluster"]
    if len(cluster) >= visual_clustering_threshold:
      if visual_features == None:
        print_status("Reading visual features (colors and edges) from file.... ")
        images = read_features_from_file(cluster, visual_features_filename, metadata_dir)
        # print_status("Extracting visual features (colors and edges) from images.... ")
        # images = extract_features(cluster, metadata_dir)
      else:
        print_status("Assign visual features (colors and edges).... ")
        images = assign_visual_features(cluster, visual_features, metadata_dir)
      print "Done.\n"

      print_status("Clustering images by visual features via k-means algorithm.... ")
      clusters = cluster_by_features(images)
      representatives_and_cluster_dict["subcluster"] = clusters.values()
      print "Done. %d subclusters for " % len(clusters), tree_node.name
    else:
      representatives_and_cluster_dict["subcluster"] = [cluster]

  #print "previously %d subclusters" % len(tree_node.subclusters)
  #tree_node.subclusters = new_subclusters
  #print "now %d subclusters" % len(tree_node.subclusters)

  if tree_node.has_hyponyms():
    for child_hyponym_node in tree_node.hyponyms:
      cluster_visually(child_hyponym_node, visual_clustering_threshold, visual_features)
  if tree_node.has_meronyms():
    for child_meronym_node in tree_node.meronyms:
      cluster_visually(child_meronym_node, visual_clustering_threshold, visual_features)

  return tree_node
