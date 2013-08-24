import sys
from flask import Flask, url_for, Response
from flask import render_template
from flask_assets import Environment, Bundle
# from flask.ext.assets import Environment, Bundle
# from flask import jsonify

# import own modules
from clustering.pipeline import get_clusters
from clustering.semantic.wordnet_searchterm_analyzer import WordnetNodeJSONEncoder
from helpers.general_helpers import print_status, load_visual_features, load_cluster_for_synsets, load_keywords_for_pictures
from helpers.general_helpers import load_cluster_representatives

app = Flask(__name__)
assets = Environment(app)

# Loading preprocessed features on startup
print_status("Loading cluster_for_synsets from mcl_clusters file... ")
cluster_for_synsets = load_cluster_for_synsets()
print "Done."
print_status("Loading keywords_for_pictures from file... ")
keywords_for_pictures = load_keywords_for_pictures()
print "Done."
print_status("Loading cluster_representatives from file... ")
cluster_representatives = load_cluster_representatives(how_many_per_cluster=6)
print "Done."
bufferedSearches = {}

@app.route("/")
def hello():
  return render_template('index.html')

def node_subclusters_empty(subcluster_structure):
  for mcl_cluster in subcluster_structure:
    if mcl_cluster["subcluster"] != [[]]:
      return False
  return True


def recursivelyCleanResult(results):
  clean_results = []
  for node in results:
    if node.hyponyms:
      node.hyponyms = recursivelyCleanResult(node.hyponyms)
    if node.meronyms:
      node.meronyms = recursivelyCleanResult(node.meronyms)
    if node.meronyms or node.hyponyms or not node_subclusters_empty(node.subclusters):
      clean_results.append(node)
  return clean_results

@app.route("/search/<searchterm>")
def search(searchterm):
  if searchterm not in bufferedSearches.keys():
    result = get_clusters(searchterm, use_meronyms=False,
                          visual_clustering_threshold=4,
                          mcl_clustering_threshold=4,
                          minimal_mcl_cluster_size=6,
                          minimal_node_size=4,
                          cluster_for_synsets=cluster_for_synsets,
                          keywords_for_pictures=keywords_for_pictures,
                          cluster_representatives=cluster_representatives)

    bufferedSearches[searchterm] = recursivelyCleanResult(result)
  return render_template('index.html', tree=bufferedSearches[searchterm])

if __name__ == "__main__":
  app.run(debug=True)
