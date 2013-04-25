#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# Script crawls available metadata from Flickr for given metadata files.
#
# Specify the FlickrAPI-Key as well as folder for metadata in the
# config file: ../config.cfg
#
# Use config.cfg.template as template for this file
#
#
# author: nicolas fricke
# mail: nicolas.fricke@student.hpi.uni-potsdam.de
################################################################################

import ConfigParser
import sys
import urllib2
import flickrapi
import time
import pprint

def parse_datafile(file_name):
  data = {}
  for line in open(file_name):
    line = line.strip()
    key, value = tuple(entry.strip() for entry in line.split(':', 1))
    data[key] = value
  return data

def url_exists(url):
  try:
    response = urllib2.urlopen(url)
  except urllib2.URLError as error:
    response = error
    return False
  return response.code == 200

def build_flickr_query(api_key, photo_id, method):
  return ('http://api.flickr.com/services/rest/'
    '?method=' + method +
    '&api_key=' + api_key +
    '&photo_id=' + photo_id +
    '&format=json')

def query_flickr(flickr, photo_id):
  metadata={}

  print "Fetching metadata for photo_id={0} (API-call! Will wait 1sec until continue)...".format(photo_id),
  time.sleep(1)
  info = flickr.photos_getInfo(photo_id=photo_id)

  #id
  metadata['photo_id'] = int(photo_id)

  #title
  if info.find('photo').find('title').text is None:
    metadata['title']   = ""
  else:
    metadata['title']   = info.find('photo').find('title').text.strip()

  #description
  if info.find('photo').find('description').text is None:
    metadata['description'] = None
  else:
    metadata['description'] = info.find('photo').find('description').text.strip()

#description
  if info.find('photo').find('dates') is None:
    metadata['dates'] = None
  else:
    metadata['dates'] = info.find('photo').find('dates')

  #tags
  metadata['tags'] = set()
  metadata['machine_tags'] = set()
  for tag in info.find('photo').getiterator('tag'):
    metadata['tags'].add(tag.attrib['raw'].strip())
    metadata['machine_tags'].add(tag.attrib['machine_tag'].strip())
  metadata['tags'] = list(metadata['tags'])
  metadata['machine_tags'] = list(metadata['machine_tags'])


  #user notes (in-photo annotations)
  metadata['notes'] = []
  for note in info.find('photo').getiterator('note'):
    metadata['notes'].append((int(note.attrib['x']), int(note.attrib['y']), int(note.attrib['w']), int(note.attrib['h']), note.text.strip()))

  #comments
  metadata['comments'] = set()
  numcomments = int(info.find('photo').find('comments').text)
  if numcomments > 0:
    print "\nFetching comments (API-call! Will wait 1sec until continue)..."
    time.sleep(1)

    comments = flickr.photos_comments_getList(photo_id=photo_id)
    for comment in comments.getiterator('comment'):
      metadata['comments'].add(comment.text.strip())
    print "Done."
  metadata['comments'] = list(metadata['comments'])

  #high-res URL
  sizes = flickr.photos_getSizes(photo_id = photo_id)
  max_width = 0
  url = ''
  for size in sizes.getiterator('size'):
    if int(size.attrib['width']) > max_width:
      max_width = int(size.attrib['width'])
      url = size.attrib['source']
  metadata['url'] = url
  print "Done."
  return metadata

def main():
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')

  api_key = config.get('Flickr API Key', 'key')
  metadata_dir = '../' + config.get('Directories', 'metadata-dir')

  # initialize pyFlickrAPI
  pyFlickrAPI = flickrapi.FlickrAPI(api_key)

  # open metadata file
  metadata_file = parse_datafile(metadata_dir + '/10-19/10/100000.txt')
  if url_exists(metadata_file.get('Web url')):
    try:
      photo_meta_data = query_flickr(pyFlickrAPI, metadata_file.get('Photo id'))
      print "Found the following metedata:\n___________________________________________________________________________\n\n"
      pp = pprint.PrettyPrinter(indent=3)
      pp.pprint(photo_meta_data)
    except flickrapi.FlickrError as e:
      print "Cannot retrieve metadata for photo_id: {0} ({1})".format(photo_id,e.message)

    print "\n\nFinished: ",time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

if __name__ == '__main__':
    main()
