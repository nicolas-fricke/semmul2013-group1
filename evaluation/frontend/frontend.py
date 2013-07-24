import sys
import os
import json
import random
from flask import Flask, url_for, Response
from flask import render_template
from flask_assets import Environment, Bundle
# from flask.ext.assets import Environment, Bundle
# from flask import jsonify

# load image urls into memory
image_urls = {}
testset_dir = '../testset'
for filename in os.listdir(testset_dir):
  if os.path.isfile(testset_dir + os.sep + filename):
    json_file = json.load(open(testset_dir + os.sep + filename, 'r'))
    try:
      for size in json_file['metadata']['sizes']['sizes']['size']:
        if size['label'] == 'Medium':
          image_urls[int(filename.split('.')[0])] = size['source']
    except KeyError:
      continue

app = Flask(__name__)
assets = Environment(app)

def choose_random_images():
  image_1_id = random.choice(image_urls.keys())
  image_2_id = image_1_id
  while image_2_id == image_1_id:
    image_1_id = random.choice(image_urls.keys())
  if image_1_id < image_2_id:
    return ({'id': image_1_id, 'url': image_urls[image_1_id]}, {'id': image_2_id, 'url': image_urls[image_2_id]})
  else:
    return ({'id': image_2_id, 'url': image_urls[image_2_id]}, {'id': image_1_id, 'url': image_urls[image_1_id]})

@app.route("/")
def hello():
  images = choose_random_images()
  return render_template('index.html', images=images)

if __name__ == "__main__":
  app.run(debug=True)
