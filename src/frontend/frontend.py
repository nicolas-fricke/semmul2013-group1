import sys
from flask import Flask, url_for, Response
from flask import render_template
# from flask.ext.assets import Environment, Bundle
# from flask import jsonify

# import own modules
from clustering.pipeline import get_clusters
from clustering.semantic.wordnet_searchterm_analyzer import WordnetNodeJSONEncoder
from helpers.general_helpers import load_visual_features

app = Flask(__name__)

# Loading preprocessed features on startup
visual_features = load_visual_features()

@app.route("/")
def hello():
  return render_template('result.html')

@app.route("/search/<searchterm>")
def search(searchterm):
  tree = get_clusters(searchterm, use_meronyms=False, visual_clustering_threshold=4, mcl_clustering_threshold=6, visual_features=visual_features)
  #return render_template('result_old.html', tree=tree, encodedtree=WordnetNodeJSONEncoder().encode(tree))
  return Response(WordnetNodeJSONEncoder().encode(tree), mimetype='application/json')

if __name__ == "__main__":
  app.run(debug=True)
