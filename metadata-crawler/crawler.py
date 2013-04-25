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
import json
import glob

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

def flickr_photos_getInfo(flickrAPI, photo_id):
  flickr_result_info = flickrAPI.photos_getInfo(photo_id=photo_id, format='json')
  photos_getInfo = json.loads(flickr_result_info[14:-1])
  return photos_getInfo

def flickr_photos_getInfo(flickrAPI, photo_id):
  flickr_result_info = flickrAPI.photos_getInfo(photo_id=photo_id, format='json')
  photos_getInfo = json.loads(flickr_result_info[14:-1])
  return photos_getInfo

def query_flickr(flickrAPI, photo_id):
  result = {}
  result['id'] = photo_id
  result['status_code'] = 200
  result['status_message'] = "Success"

  result['metadata'] = {}
  print "Fetching metadata for photo_id={0} (API-call! Will wait 1sec until continue)...".format(photo_id),
  time.sleep(1)
  result['metadata']['info'] = flickr_photos_getInfo(flickrAPI, photo_id)

  return json.dumps(result)

def find_metafiles_to_process(metadata_path):
  txt_files  = glob.glob(metadata_path + '/*/*/*.txt')
  json_files = glob.glob(metadata_path + '/metadata/*/*/*.json')
  return [txt_file for txt_file in txt_files if (txt_file[:-3] + 'json') not in json_files]

def main():
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')

  api_key = config.get('Flickr API Key', 'key')
  metadata_dir = '../' + config.get('Directories', 'metadata-dir')

  # initialize pyFlickrAPI
  pyFlickrAPI = flickrapi.FlickrAPI(api_key)

  metafiles_paths = find_metafiles_to_process(metadata_dir)

  for metafile_path in metafiles_paths:
    print "Parsing file: {0}".format(metafile_path)
    metafile = parse_datafile(metafile_path)
    photo_id = metafile.get('Photo id')
    if url_exists(metafile.get('Web url')):
      try:
        photo_metadata = query_flickr(pyFlickrAPI, photo_id)
        print "Metadata for photo {0} sucessfully crawled".format(photo_id)
      except flickrapi.FlickrError as e:
        print "Cannot retrieve metadata for photo_id: {0} ({1})".format(photo_id,e.message)
    else:
      print "Photo {0} has been deleted".format(photo_id)
      photo_metadata = json.dumps({"id": photo_id, "status_code": 404, "status_message": "Not Found"})

    pp = pprint.PrettyPrinter(indent=3)
    pp.pprint(json.loads(photo_metadata))

    print "\n\nFinished: ",time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

if __name__ == '__main__':
    main()
