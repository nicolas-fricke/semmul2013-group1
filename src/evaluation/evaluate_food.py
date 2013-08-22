import sys
from sets import Set
import sqlite3
import json
import argparse
# import own modules
import clustering.pipeline as pipeline
from helpers.general_helpers import print_status
import helpers.general_helpers as general_helpers

def recursively_collect_images(siblings):
  sibling_images = Set()
  for synset in siblings:
    sibling_images |= Set([image[0].split('\\')[-1].split('.')[0] for mcl_cluster in synset.subclusters for visual_cluster in mcl_cluster['subcluster'] for image in visual_cluster])
    sibling_images |= recursively_collect_images(synset.hyponyms)
  return sibling_images

def retrieveTestsetResults(database_file):
  con = sqlite3.connect(database_file)

  # Positive votes (showing food)
  cur = con.cursor()
  cur.execute('''SELECT image_id, count(*) as votes, sum(contains_food) as positive_votes
                 FROM semmul_images
                 GROUP BY image_id
                 HAVING votes - positive_votes < 0.5 * votes
                 ORDER BY votes DESC;''')

  positive_ids = Set([str(row[0]) for row in cur.fetchall()])

  # Negative votes (not showing food)
  cur = con.cursor()
  cur.execute('''SELECT image_id, count(*) as votes, sum(contains_food) as positive_votes
                 FROM semmul_images
                 GROUP BY image_id
                 HAVING votes - positive_votes >= 0.5 * votes
                 ORDER BY votes DESC;''')

  negative_ids = Set([str(row[0]) for row in cur.fetchall()])

  return positive_ids, negative_ids

def main(args):
  print_status("Checking images against testset:\n")

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
  # image_tree = get_searchtrees_with_filenames("food", use_meronyms=False, minimal_node_size=1)
  image_tree = pipeline.get_clusters("food", use_meronyms=False,
                                     visual_clustering_threshold=10000,
                                     mcl_clustering_threshold=4,
                                     minimal_mcl_cluster_size=2,
                                     minimal_node_size=2,
                                     visual_features=visual_features,
                                     cluster_for_synsets=cluster_for_synsets,
                                     keywords_for_pictures=keywords_for_pictures,
                                     cluster_representatives=cluster_representatives)

  sys.stdout.write("Collecting images from tree... \n")
  result_ids = recursively_collect_images(image_tree)

  sys.stdout.write("Loading testset from database... \n")
  testset_positive_ids, testset_negative_ids = retrieveTestsetResults(args.database_file)

  sys.stdout.write("Comparing result images to testset... \n")

  result_size           = len(result_ids)
  testset_positive_size = len(testset_positive_ids)
  testset_negative_size = len(testset_negative_ids)

  true_positives  = 0
  false_positives = 0

  for result_id in result_ids:
    if result_id in testset_positive_ids:
      true_positives += 1
      testset_positive_ids.remove(result_id)
    if result_id in testset_negative_ids:
      false_positives += 1
      testset_negative_ids.remove(result_id)

  false_negatives = len(testset_positive_ids)

  precision = float(true_positives) / (true_positives + false_positives)
  recall = float(true_positives) / (true_positives + false_negatives)

  sys.stdout.write("Done:\n\n")

  sys.stdout.write("Testset size:    %d\n\n" % (testset_positive_size + testset_negative_size))
  sys.stdout.write("Result size:     %d\n" % result_size)
  sys.stdout.write("Real positives:  %d\n\n" % testset_positive_size)
  sys.stdout.write("True Positives:  %d\n" % true_positives)
  sys.stdout.write("True Negatives:  ???\n")
  sys.stdout.write("False Positives: %d\n" % false_positives)
  sys.stdout.write("False Negatives: %d\n\n" % false_negatives)
  sys.stdout.write("Precision:       %f (tp / (tp + fp))\n" % precision)
  sys.stdout.write("Recall:          %f (tp / (tp + fn))\n" % recall)
  sys.stdout.write("F-Measure:       %f (2 * (p * r / (p + r)))\n" % (2 * (float(precision) * float(recall)) / (precision + recall)))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Frontend for the Flickr image similarity evaluation programm')
  parser.add_argument('-d','--database-file', help='Path to the database file (phase 1)', required=True)
  args = parser.parse_args()
  main(args)