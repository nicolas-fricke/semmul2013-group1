import sys
from sets import Set
import sqlite3
import json
import argparse
# import own modules
import clustering.pipeline as pipeline
from helpers.general_helpers import print_status
import helpers.general_helpers as general_helpers

# Development
import cPickle as pickle

class ImageTree(object):
  def __init__(self, parent, type):
    self.parent = parent
    self.type = type
    self.children = []
    self.image_ids = []

def recursively_parse_result_tree(pipeline_tree, parent_image_id_tree_node):
  for wordnet_node in pipeline_tree:
    new_synset_node = ImageTree(parent_image_id_tree_node, 'synset')
    parent_image_id_tree_node.children.append(new_synset_node)
    for mcl_cluster in wordnet_node.subclusters:
      new_mcl_node =  ImageTree(new_synset_node, 'mcl')
      new_synset_node.children.append(new_mcl_node)
      for visual_cluster in mcl_cluster['subcluster']:
        for image_tuple in visual_cluster:
          image_id = image_tuple[0].split('\\')[-1].split('.')[0]
          new_mcl_node.image_ids.append(image_id)
    recursively_parse_result_tree(wordnet_node.hyponyms, new_synset_node)
  return parent_image_id_tree_node

def parse_result_tree(pipeline_tree):
  return recursively_parse_result_tree(pipeline_tree, ImageTree(None, 'root'))


def retrieveTestsetResults(database_file):
  con = sqlite3.connect(database_file)

  # Retrieve id tuples of same object images
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
                      GROUP BY image_1_id, image_2_id, visual_similarity, semantic_similarity
                    ) AS b
                  WHERE s.image_1_id = a.image_1_id
                  AND s.image_2_id = a.image_2_id
                  AND a.image_1_id = b.image_1_id
                  AND a.image_2_id = b.image_2_id
                  AND all_votes = same_votes
                  AND s.semantic_similarity == 'same_object'
                  GROUP BY s.image_1_id, s.image_2_id; ''')

  same_object_ids = Set([(str(row[0]), str(row[1])) for row in cur.fetchall()])

  # Retrieve id tuples of same object and same context images
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
                        GROUP BY image_1_id, image_2_id, visual_similarity, semantic_similarity
                      ) AS b
                    WHERE s.image_1_id = a.image_1_id
                    AND s.image_2_id = a.image_2_id
                    AND a.image_1_id = b.image_1_id
                    AND a.image_2_id = b.image_2_id
                    AND all_votes = same_votes
                    AND s.semantic_similarity == 'same_context'
                    GROUP BY s.image_1_id, s.image_2_id; ''')

  same_context_ids = Set([(str(row[0]), str(row[1])) for row in cur.fetchall()])

  same_object_same_context_ids  =  same_context_ids | same_object_ids

  return same_object_ids, same_object_same_context_ids

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
                                     visual_clustering_threshold=4,
                                     mcl_clustering_threshold=4,
                                     minimal_mcl_cluster_size=6,
                                     minimal_node_size=4,
                                     visual_features=visual_features,
                                     cluster_for_synsets=cluster_for_synsets,
                                     keywords_for_pictures=keywords_for_pictures,
                                     cluster_representatives=cluster_representatives)
  # pipeline_result = pickle.load(open('image_tree.pickle', 'r'))

  print_status("Parsing result tree to easier accessible format...")
  parsed_result_tree = parse_result_tree(pipeline_result)


  sys.stdout.write("Loading testset from database... \n")
  same_object_ids, same_object_same_context_ids = retrieveTestsetResults(args.database_file)

  sys.stdout.write("Comparing result images to testset... \n")

  ### TODO ###


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Frontend for the Flickr image similarity evaluation programm')
  parser.add_argument('-d','--database-file', help='Path to the database file (phase 1)', required=True)
  args = parser.parse_args()
  main(args)