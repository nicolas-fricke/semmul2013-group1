import sys
import os
import json
import random
import argparse
from flask import Flask, url_for, request, _app_ctx_stack, g, \
  redirect, abort, flash, session
from flask import Response, render_template
from flask_assets import Environment, Bundle
import sqlite3
import contextlib

# configuration:
# database:
DATABASE = '/tmp/presorting-evaluation.db'
SECRET_KEY = '123 - thats a hyper secret key'
# server:
SERVER_NAME = 'localhost:5000'
DEBUG = True


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('SEMMUL_EVALUATION_SETTINGS', silent=True)
assets = Environment(app)


def init_db():
  """Creates the database tables."""
  with app.app_context():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

def get_db():
  """Opens a new database connection if there is none yet for the
  current application context.
  """
  top = _app_ctx_stack.top
  if not hasattr(top, 'sqlite_db'):
    sqlite_db = sqlite3.connect(app.config['DATABASE'])
    sqlite_db.row_factory = sqlite3.Row
    top.sqlite_db = sqlite_db
  return top.sqlite_db

def add_get_param_to_url(url, parameter_name, parameter_value):
  if url.find("?") == -1:
    return url + "?" + parameter_name + "=" + parameter_value
  else:
    return url + "&" + parameter_name + "=" + parameter_value

@app.teardown_appcontext
def close_db_connection(exception):
  """Closes the database again at the end of the request."""
  top = _app_ctx_stack.top
  if hasattr(top, 'sqlite_db'):
    top.sqlite_db.close()

@app.route("/")
def index():
  image = choose_random_image()
  return render_template('index.html', image=image)

@app.route('/add', methods=['POST'])
def add_entry():
  db = get_db()
  db.execute('insert into semmul_images (image_id, contains_food, nicname, email) values (?, ?, ?, ?)',
             [request.form['image_id'], request.form['image_food'], request.form['username'], request.form['email']])
  db.commit()
  flash('New entry was successfully posted')
  redirect_url = '/'
  if request.form['username'] != '':
    redirect_url = add_get_param_to_url(redirect_url, 'nicname', request.form['username'])
  if request.form['email'] != '':
    redirect_url = add_get_param_to_url(redirect_url, 'email', request.form['email'])
  return redirect(redirect_url)

def choose_random_image():
  image_id = random.choice(image_urls.keys())
  return {'id': image_id, 'url': image_urls[image_id]}

def load_image_urls(testset_file):
  return json.load(open(testset_file, 'r'))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Frontend for the Flickr image similarity evaluation programm')
  parser.add_argument('-t','--testset-file', help='Path to the testset JSON file', required=True)
  parser.add_argument('-p','--port', type=int, help='Port the server will run on')
  parser.add_argument('-db','--db-path', help='Path for the Sqlite database file')
  parser.add_argument('-k','--secret-key', help='The secret key')
  parser.add_argument('--production', help='Run program in production mode', action="store_true")
  args = parser.parse_args()
  if args.production: app.debug = False
  if args.port: app.config.update(SERVER_NAME = 'localhost:' + str(args.port))
  if args.secret_key: app.config.update(SECRET_KEY = args.secret_key)
  if args.db_path: app.config.update(DATABASE = args.db_path)
  global image_urls
  image_urls = load_image_urls(args.testset_file)
  init_db()
  app.run(debug=True)
