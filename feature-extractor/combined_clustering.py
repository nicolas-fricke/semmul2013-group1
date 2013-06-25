import argparse
import ConfigParser
import json
import numpy as np
from collections import defaultdict
from SimpleCV import Image
from math import log, pow
from scipy.cluster.hierarchy import fclusterdata as hierarchial_cluster
from Pycluster import kcluster
# Import own module helpers
import sys
sys.path.append('../helpers')
from general_helpers import *
from visual_helpers import *
from color_clustering import extract_colors
from edge_clustering import extract_edges


def main(argv):
  parser = argparse.ArgumentParser(description='ADD DESCRIPTION TEXT.')
  parser.add_argument('-p','--preprocessed', dest='use_preprocessed_data', action='store_true',
                   help='If specified, use preprocessed image data, otherwise download and process images and save values to file for next use')
  args = parser.parse_args()

  print_status("Use preprocessed data: " + str(args.use_preprocessed_data) + "\n\n")

  if not args.use_preprocessed_data:
    # import configuration
    config = ConfigParser.SafeConfigParser()
    config.read('../config.cfg')

    api_key = config.get('Flickr API Key', 'key')
    metadata_dir = '../' + config.get('Directories', 'metadata-dir')

    metajson_files = find_metajsons_to_process(metadata_dir)

    print_status("Reading metadata files, loading images and calculating color and edge histograms.... ")
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

        data = extract_colors(image, data, 1)
        data = extract_edges(image, data, 1)
        images.append(data)

        file_number += 1
      if file_number >= 100:
        break
    print "Done."
    save_object(images, "color_and_edge_features.pickle")
  else:
    images = load_object("color_and_edge_features.pickle")

  print_status("Building data structure for clustering.... ")
  colors = []
  edges = []
  for image_data in images:
    colors.append(image_data["colors"])
    edges.append(image_data["edge-angles"] + image_data["edge-lengths"])
  print "Done."

  print_status("Clustering images by color histograms via k-means algorithm.... ")
  #clustered_images = hierarchial_cluster(colors, 0.71, criterion='inconsistent', metric='euclidean')#distance_function)
  k_color = 2
  clustered_images_by_color, error, _ = kcluster(colors, k_color, npass=5)
  previous_error = pow(error,2)
  while 1/(log(k_color+0.000001)*error) > 1/(log(k_color-0.999999)*previous_error):
  #while error < 0.9 * previous_error:
    k_color += 1 
    previous_error = error
    clustered_images_by_color, error, _ = kcluster(colors, k_color, npass=5)
  k_color -= 1
  clustered_images_by_color, error, _ = kcluster(colors, k_color, npass=10)
  print "Done. %d Clusters with error %d" % (k_color, error)

  print_status("Clustering images by edge histograms via k-means algorithm.... ")
  k_edges = 2
  clustered_images_by_edges, error, _ = kcluster(edges, k_edges, npass=5)
  previous_error = error * 10
  #while 1/(log(k_edges+0.0000001)*error) > 1/(log(k_edges-0.999999)*previous_error):
  while error < 0.85 * previous_error:
    k_edges += 1
    previous_error = error
    clustered_images_by_edges, error, _ = kcluster(edges, k_edges, npass=5)
  k_edges -= 1
  clustered_images_by_edges, error, nfound = kcluster(edges, k_edges, npass=10)
  print "Done. %d Clusters with error %f" % (k_edges, error)

  #DO LATE FUSION
  print_status("Displaying clusters (simple intersection of color and edge clusters")
  clusters = defaultdict(list)
  for index, cluster_color in enumerate(clustered_images_by_color):
    cluster_edges = clustered_images_by_edges[index]
    clusters[cluster_color + cluster_edges * k_color].append(images[index])

  write_clusters_to_html(clusters, open_in_browser=True)

if __name__ == '__main__':
    main(sys.argv[1:])