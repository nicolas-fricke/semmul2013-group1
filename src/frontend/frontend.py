import sys
from flask import Flask, url_for, Response
from flask import render_template
# from flask.ext.assets import Environment, Bundle
# from flask import jsonify


sys.path.append('../semantic-clustering')
from pipeline import *

app = Flask(__name__)

@app.route("/")
def hello():
  return render_template('result.html')

@app.route("/search/<searchterm>")
def search(searchterm):
  tree = get_clusters(searchterm)
  #return render_template('result.html', tree=WordnetNodeJSONEncoder().encode(tree), mimetype='application/json')
  return render_template('result.html', tree=tree, mimetype='application/json')

if __name__ == "__main__":
  app.run(debug=True)
