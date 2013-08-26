import sys
import sqlite3
import json
import argparse
import copy

# import own modules
import clustering.pipeline as pipeline
from helpers.general_helpers import print_status
import helpers.general_helpers as general_helpers
import clustering.visual.combined_clustering as combined_clustering

# Development
import cPickle as pickle

def recursively_collect_images(siblings):
  sibling_image_tuples = {}
  for synset in siblings:
    for subcluster in synset.subclusters:
      for subsubcluster in subcluster['subcluster']:
        for image_tuple in subsubcluster:
          image_id  = image_tuple[0].split('\\')[-1]
          image_url = image_tuple[1]
          sibling_image_tuples[image_id] = image_url

    sibling_image_tuples = dict(sibling_image_tuples, **recursively_collect_images(synset.hyponyms))
  return sibling_image_tuples

def flatten_result_tree(pipeline_tree, annotated_food_dict, size_from_id=0, size_to_id=-1):
  # collect all image tuples
  image_dict = recursively_collect_images(pipeline_tree)
  image_tuples = [[image_id, image_url] for image_id, image_url in image_dict.iteritems() if image_id.split('.')[0] in annotated_food_dict.keys()][size_from_id:size_to_id]
  # empty first tree node
  pipeline_tree_node = pipeline_tree[0]
  pipeline_tree_node.hyponyms = []
  pipeline_tree_node.meronyms = []
  pipeline_tree_node.associated_pictures = image_tuples
  pipeline_tree_node.name = "combined_node"
  pipeline_tree_node.definition = "Contains all images within one MCL cluster"
  pipeline_tree_node.subclusters = [{'synsets': 'all', 'subcluster': list(image_tuples)}]

  # and return flattened tree node as expected list
  return pipeline_tree_node

def retrieveTestsetResults(database_file):
  con = sqlite3.connect(database_file)

  # Retrieve id tuples visually similar image tuples
  cur = con.cursor()
  cur.execute(''' SELECT s.image_1_id, s.image_2_id
                    FROM
                      semmul_image_similarity AS s,
                      (
                        SELECT image_1_id, image_2_id, COUNT(*) AS all_votes
                        FROM semmul_image_similarity
                        GROUP BY image_1_id, image_2_id
                      ) AS a,
                      (
                        SELECT image_1_id, image_2_id, COUNT(*) AS same_votes
                        FROM semmul_image_similarity
                        GROUP BY image_1_id, image_2_id, visual_similarity
                      ) AS b
                    WHERE s.image_1_id = a.image_1_id
                    AND s.image_2_id = a.image_2_id
                    AND a.image_1_id = b.image_1_id
                    AND a.image_2_id = b.image_2_id
                    AND all_votes = same_votes
                    AND s.visual_similarity == 'visually_similar'
                    GROUP BY s.image_1_id, s.image_2_id; ''')

  visually_similar_tuples = set([(str(row[0]), str(row[1])) for row in cur.fetchall()])


  # Retrieve id tuples of visually not similar image tuples
  cur = con.cursor()
  cur.execute(''' SELECT s.image_1_id, s.image_2_id
                    FROM
                      semmul_image_similarity AS s,
                      (
                        SELECT image_1_id, image_2_id, COUNT(*) AS all_votes
                        FROM semmul_image_similarity
                        GROUP BY image_1_id, image_2_id
                      ) AS a,
                      (
                        SELECT image_1_id, image_2_id, COUNT(*) AS same_votes
                        FROM semmul_image_similarity
                        GROUP BY image_1_id, image_2_id, visual_similarity
                      ) AS b
                    WHERE s.image_1_id = a.image_1_id
                    AND s.image_2_id = a.image_2_id
                    AND a.image_1_id = b.image_1_id
                    AND a.image_2_id = b.image_2_id
                    AND all_votes = same_votes
                    AND s.visual_similarity == 'not_visually_similar'
                    GROUP BY s.image_1_id, s.image_2_id; ''')

  visually_different_tuples = set([(str(row[0]), str(row[1])) for row in cur.fetchall()])

  return visually_similar_tuples, visually_different_tuples

def both_ids_are_found(image_id_tuple, visual_clusters):
  for cluster_outer in visual_clusters:
    if image_id_tuple[0] in cluster_outer:
      for cluster_inner in visual_clusters:
        if image_id_tuple[1] in cluster_inner:
          return True
      return False
  return False

def one_cluster_contains_both_ids(image_id_tuple, visual_clusters):
  for cluster in visual_clusters:
    if image_id_tuple[0] in cluster and image_id_tuple[1] in cluster:
      return True
  return False

def main(args):
  # Loading preprocessed features on startup
  print_status("Loading visual_features from file... ")
  visual_features = general_helpers.load_visual_features()
  print "Done."
  print_status("Loading cluster_for_synsets from mcl_clusters file... ")
  cluster_for_synsets = general_helpers.load_cluster_for_synsets()
  print "Done."
  print_status("Loading keywords_for_pictures from file... ")
  keywords_for_pictures = general_helpers.load_keywords_for_pictures()
  print "Done."
  print_status("Loading cluster_representatives from file... ")
  cluster_representatives = general_helpers.load_cluster_representatives(how_many_per_cluster=6)
  print "Done loading preprocessed data."

  print_status("Checking images against testset:\n")
  print_status("Retrieving clusters... \n")
  pipeline_result = pipeline.get_clusters("food", use_meronyms=False,
                                     visual_clustering_threshold=100000,
                                     mcl_clustering_threshold=4,
                                     minimal_mcl_cluster_size=6,
                                     minimal_node_size=4,
                                     visual_features=visual_features,
                                     cluster_for_synsets=cluster_for_synsets,
                                     keywords_for_pictures=keywords_for_pictures,
                                     cluster_representatives=cluster_representatives)


  # # Comment in to load preprocessed pipeline_result for dev mode
  # pipeline_result = pickle.load(open('image_tree.pickle', 'r'))

  annotated_food_dict = json.load(open(args.food_id_file, 'r'))

  print_status("Flattening result tree... \n")
  flattened_mcl_tree = flatten_result_tree(pipeline_result, annotated_food_dict, size_from_id=0, size_to_id=-1)
  image_counter = len(flattened_mcl_tree.subclusters[0]['subcluster'])

  print_status("Loading visual_features from file... \n")
  visual_features = general_helpers.load_visual_features()

  true_positives_total  = []
  false_negatives_total = []
  true_negatives_total  = []
  false_positives_total = []

  for i in range(0, 10):
    print_status("Calculating visual clusters (%d x)... \n" % i)
    visually_clustered_result = combined_clustering.cluster_visually(copy.deepcopy(flattened_mcl_tree),
                                                                     visual_clustering_threshold=4,
                                                                     visual_features=visual_features)
  
    print_status("Convert visual clusters to simpler structure... \n")
    visual_clusters = []
    for visual_cluster in visually_clustered_result.subclusters[0]['subcluster']:
      visual_clusters.append(set([image_tuple[0].split('\\')[-1].split('.')[0] for image_tuple in visual_cluster]))
  
    print_status("Done clustering %d images into %d visual clusters. \n" % (image_counter, len(visual_clusters)))
  
    # # Comment in to load preprocessed visual_clusters for dev mode
    # visual_clusters = pickle.load(open('visual_clusters.pickle', 'r'))
  
    print_status("Loading testset from database... \n")
    visually_similar_tuples, visually_different_tuples = retrieveTestsetResults(args.database_file)
  
    print_status("Comparing clusters to testset... \n")

    true_negatives  = 0
    false_positives = 0
    true_positives  = 0
    false_negatives = 0

    print_status("Starting with visually similar tuples... \n")
    for id_tuple in visually_similar_tuples:
      if both_ids_are_found(id_tuple, visual_clusters):
        if one_cluster_contains_both_ids(id_tuple, visual_clusters):
          true_negatives += 1
        else:
          false_positives += 1
  
    print_status("Now checking different image tuples... \n")
    for id_tuple in visually_different_tuples:
      if both_ids_are_found(id_tuple, visual_clusters):
        if one_cluster_contains_both_ids(id_tuple, visual_clusters):
          false_negatives += 1
        else:
          true_positives += 1

    true_positives_total.append(true_positives)
    false_negatives_total.append(false_negatives)
    true_negatives_total.append(true_negatives)
    false_positives_total.append(false_positives)

  average_true_positives  = float(sum(true_positives_total))  / len(true_positives_total)
  average_false_negatives = float(sum(false_negatives_total)) / len(false_negatives_total)
  average_true_negatives  = float(sum(true_negatives_total))  / len(true_negatives_total)
  average_false_positives = float(sum(false_positives_total)) / len(false_positives_total)

  precision = float(average_true_positives) / (average_true_positives + average_false_positives)
  recall    = float(average_true_positives) / (average_true_positives + average_false_negatives)

  print_status("Done!\n\n")
  sys.stdout.write("Testset contains %5d visually similar   image tuples \n" % len(visually_similar_tuples))
  sys.stdout.write("And there are    %5d visually different image tuples \n\n" % len(visually_different_tuples))

  sys.stdout.write("Average true  positives: %f \n"   % average_true_positives)
  sys.stdout.write("Average false negatives: %f \n"   % average_false_negatives)
  sys.stdout.write("Average true  negatives: %f \n"   % average_true_negatives)
  sys.stdout.write("Average false positives: %f \n\n" % average_false_positives)

  sys.stdout.write("Precision: %f (tp / (tp + fp))\n" % precision)
  sys.stdout.write("Recall:    %f (tp / (tp + fn))\n" % recall)
  sys.stdout.write("F-Measure: %f (2 * (p * r / (p + r)))\n" % (2 * (float(precision) * float(recall)) / (precision + recall)))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Frontend for the Flickr image similarity evaluation programm')
  parser.add_argument('-d','--database-file', help='Path to the database file (phase 2)', required=True)
  parser.add_argument('-f','--food-id-file', help='Path to the json file with for food-annotated images', required=True)
  args = parser.parse_args()
  main(args)