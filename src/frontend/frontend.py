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

app = Flask(__name__)
assets = Environment(app)

# Loading preprocessed features on startup
print_status("Loading visual_features from file... ")
visual_features = load_visual_features()
print "Done."
print_status("Loading cluster_for_synsets from mcl_clusters file... ")
cluster_for_synsets = load_cluster_for_synsets()
print "Done."
print_status("Loading keywords_for_pictures from file... ")
keywords_for_pictures = load_keywords_for_pictures()
print "Done."
bufferedSearches = {}

@app.route("/")
def hello():
  return render_template('index.html')

@app.route("/search/<searchterm>")
def search(searchterm):
  if searchterm not in bufferedSearches.keys():
    bufferedSearches[searchterm] = get_clusters(searchterm, use_meronyms=False, visual_clustering_threshold=4, mcl_clustering_threshold=6,
                                   visual_features=visual_features,
                                   cluster_for_synsets=cluster_for_synsets,
                                   keywords_for_pictures=keywords_for_pictures)
  return render_template('index.html', tree=bufferedSearches[searchterm])

if __name__ == "__main__":
  app.run(debug=True)
