import argparse
import ConfigParser
import json
import numpy as np
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

def extract_features(image_cluster, metadata_dir):
  images = []
  for metajson_file, _ in image_cluster:
    relative_path_to_json = construct_path_to_json(metajson_file)
    full_path_to_json = metadata_dir + relative_path_to_json
    metadata = parse_json_file(full_path_to_json)

    if metadata["stat"] == "ok":
      data = {}
      url = get_small_image_url(metadata)
      data["image_id"]  = metadata["id"]
      data["file_path"] = full_path_to_json
      data["url"]       = url
      try:
        image = Image(url).toHSV()
      except Exception:
        continue

      data = extract_colors(image, data, 5)
      data = extract_edges(image, data, 5)
      images.append(data)
  return images


def read_features_from_file(cluster, json_filename):
  images = []
  json_file = parse_json_file(json_filename)
  for picture_json_filename, _ in cluster:
    picture_json_file = parse_json_file(picture_json_filename)

    if picture_json_file["stat"] == "ok":
      data = json_file[picture_json_file["image_id"]]
      data["image_id"] = picture_json_file["image_id"]
    images.append(data)

  return images


def cluster_by_single_feature(feature_matrix):
  k = 1
  error = 1
  previous_error = 1
  while (k == 2 or 1/log(k+0.000001)*error > 1/log(k-0.999999)*previous_error) and k < len(feature_matrix):
  #while error < 0.9 * previous_error:
    clustered_images_by_color, error, _ = kcluster(feature_matrix, k, npass=5)
    k += 1
    previous_error = error
  k -= 1

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


def cluster_visually(tree_node, visual_clustering_threshold=8):
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  metadata_dir = config.get('Directories', 'metadata-dir')
  visual_features_filename = config.get('Filenames for Pickles', 'visual_features_filename')

  new_subclusters = []
  for cluster in tree_node.subclusters:
    if len(cluster) >= visual_clustering_threshold:
      print_status("Extracting visual features (colors and edges) from images.... ")
      #images = read_features_from_file(cluster, visual_features_filename)
      images = extract_features(cluster, metadata_dir)
      print "Done.\n"

      print_status("Clustering images by visual features via k-means algorithm.... ")
      clusters = cluster_by_features(images)
      new_subclusters.append(clusters.values())
      print "Done. %d subclusters for " % len(clusters), tree_node.name
    else:
      new_subclusters.append([cluster])

  #print "previously %d subclusters" % len(tree_node.subclusters)
  tree_node.subclusters = new_subclusters
  #print "now %d subclusters" % len(tree_node.subclusters)

  if tree_node.has_hyponyms():
    for child_hyponym_node in tree_node.hyponyms:
      cluster_visually(child_hyponym_node)
  if tree_node.has_meronyms():
    for child_meronym_node in tree_node.meronyms:
      cluster_visually(child_meronym_node)

  return tree_node


def parse_command_line_arguments():
  parser = argparse.ArgumentParser(description='ADD DESCRIPTION TEXT.')
  parser.add_argument('-p','--preprocessed', dest='use_preprocessed_data', action='store_true',
                   help='If specified, use preprocessed image data, otherwise download and process images and save values to file for next use')
  parser.add_argument('-d','--directory_to_preprocess', dest='directory_to_preprocess', type=str,
                      help='Specifies the directory which we want to preprocess')
  parser.add_argument('-r','--read_images_from_disk', dest='read_images_from_disk', action='store_true',
                      help='Specifies whether image files should be read from disk rather than downloaded from flickr, specify image path in config file')
  args = parser.parse_args()
  return args


def main(argv):
  arguments = parse_command_line_arguments()

  print_status("Use preprocessed data: " + str(arguments.use_preprocessed_data) + "\n\n")

  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  #color_and_edge_features_filename = config.get('Filenames for Pickles', 'color_and_edge_features_filename')
  visual_features_filename = config.get('Filenames for Pickles', 'visual_features_filename')
  downloaded_images_dir = config.get('Directories', 'downloaded-images-dir')

  if not arguments.use_preprocessed_data:

    metadata_dir = config.get('Directories', 'metadata-dir') 
    if arguments.directory_to_preprocess:
      metadata_dir += arguments.directory_to_preprocess
      metajson_files = find_metajsons_to_process_in_dir(metadata_dir)
      visual_features_filename = visual_features_filename.replace('##', arguments.directory_to_preprocess.split('/')[-1])
    else:
      metajson_files = find_metajsons_to_process(metadata_dir)
      visual_features_filename = visual_features_filename.replace('##', 'all')

    print_status("Reading metadata files, loading images and calculating color and edge histograms.... \n")
    images = {}
    for metajson_file in metajson_files:

      metadata = parse_json_file(metajson_file)
      print_status("ID: " + metadata["id"] + " File number: " + metajson_file + "\n")
      if metadata["stat"] == "ok":
        #if not tag_is_present("car", metadata["metadata"]["info"]["tags"]["tag"]):
        #  continue
        data = {}
        url      = get_small_image_url(metadata)
        image_id = metadata["id"]
        data["file_path"] = metajson_file
        data["url"]       = url

        try:
          if arguments.read_images_from_disk:
            image_filename = metajson_file.split('/')[-1].replace('.json', '.jpg')
            image_path = downloaded_images_dir + '/' + image_filename
            image = Image(image_path).toHSV()
          else:
            image = Image(url).toHSV()
        except Exception:
          print "Could not get image:", metadata["id"]
          continue

        data = extract_colors(image, data, 5)
        data = extract_edges(image, data, 5)
        images[image_id] = data

        how_many_added += 1

        if how_many_added >= 1000:
          print_status("Done with " + str(file_number - index_to_start) + " of " + str(index_to_stop - index_to_start) + "\n")
          file_name = visual_features_filename + str(file_number) + ".json"
          write_json_file(images, file_name)
          images = {}
          how_many_added = 0

      else:
        print "Status was not ok:", metadata["id"]

    print "Done."
    write_json_file(images, visual_features_filename)

if __name__ == '__main__':
    main(sys.argv[1:])