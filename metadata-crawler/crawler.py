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

def flickr_photos_getInfo_title(flickr_result_info):
  #title
  if flickr_result_info.find('photo').find('title').text is None:
    return ""
  else:
    return flickr_result_info.find('photo').find('title').text.strip()

def flickr_photos_getInfo_description(flickr_result_info):
  #description
  if flickr_result_info.find('photo').find('description').text is None:
    return None
  else:
    return flickr_result_info.find('photo').find('description').text.strip()

def flickr_photos_getInfo_dates(flickr_result_info):
  if flickr_result_info.find('photo').find('dates') is None:
    return None
  else:
    return flickr_result_info.find('photo').find('dates')

def flickr_photos_getInfo_tags_and_machine_tags(flickr_result_info):
  tags = set()
  machine_tags = set()
  for tag in flickr_result_info.find('photo').getiterator('tag'):
    tags.add(tag.attrib['raw'].strip())
    machine_tags.add(tag.attrib['machine_tag'].strip())
  return list(tags), list(machine_tags)

def flickr_photos_getInfo_notes(flickr_result_info):
  notes = []
  for note in flickr_result_info.find('photo').getiterator('note'):
    notes.append((int(note.attrib['x']), int(note.attrib['y']), int(note.attrib['w']), int(note.attrib['h']), note.text.strip()))

def flickr_photos_getInfo_comments(flickr_result_info, flickrAPI, photo_id):
  comments = set()
  numcomments = int(flickr_result_info.find('photo').find('comments').text)
  if numcomments > 0:
    print "\nFetching comments (API-call! Will wait 1sec until continue)..."
    time.sleep(1)

    result_comments = flickrAPI.photos_comments_getList(photo_id=photo_id)
    for comment in result_comments.getiterator('comment'):
      comments.add(comment.text.strip())
    print "Done fetching comments."
  return list(comments)

def flickr_photos_getInfo_url(flickrAPI, photo_id):
  sizes = flickrAPI.photos_getSizes(photo_id = photo_id)
  max_width = 0
  url = ''
  for size in sizes.getiterator('size'):
    if int(size.attrib['width']) > max_width:
      max_width = int(size.attrib['width'])
      url = size.attrib['source']
  return url

def query_flickr(flickrAPI, photo_id):
  metadata={}

  print "Fetching metadata for photo_id={0} (API-call! Will wait 1sec until continue)...".format(photo_id),
  time.sleep(1)
  flickr_result_info = flickrAPI.photos_getInfo(photo_id=photo_id)

  metadata['photo_id'] = int(photo_id)
  metadata['title'] = flickr_photos_getInfo_title(flickr_result_info)
  metadata['description'] = flickr_photos_getInfo_description(flickr_result_info)
  metadata['dates'] = flickr_photos_getInfo_dates(flickr_result_info)
  metadata['tags'], metadata['machine_tags'] = flickr_photos_getInfo_tags_and_machine_tags(flickr_result_info)
  metadata['notes'] = flickr_photos_getInfo_notes(flickr_result_info)
  metadata['comments'] = flickr_photos_getInfo_comments(flickr_result_info, flickrAPI, photo_id)
  metadata['url'] = flickr_photos_getInfo_url(flickrAPI, photo_id)

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
