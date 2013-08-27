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

def flickr_parse_json(jsonString):
  return json.loads(jsonString[14:-1])

def flickr_photos_getInfo(flickrAPI, photo_id):
  flickr_result_info = flickrAPI.photos_getInfo(photo_id=photo_id, format='json')
  photos_getInfo = json.loads(flickr_result_info[14:-1])
  return photos_getInfo

def print_status(message):
  sys.stdout.write(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + " - ")
  sys.stdout.write(message)
  sys.stdout.flush()

def query_flickr(flickrAPI, photo_id):
  result = {}
  result['id'] = photo_id

  print_status("Fetching photos_getInfo for photo_id={0} (API-call! Will wait 1sec until continue)... ".format(photo_id))
  attempts = 0
  while True:
    attempts += 1
    try:
      time.sleep(1)
      info = flickr_parse_json(flickrAPI.photos_getInfo(photo_id=photo_id, format='json'))
      break
    except Exception as e:
      print_status("\nURLError, retrying (attempt {0})... ".format(attempts))
  print "Done."

  if info['stat'] == 'ok':
    result['status_code'] = 200
    result['stat'] = "ok"
    result['message'] = "Success"

    result['metadata'] = {}
    result['metadata']['info'] = info['photo']

    print_status("Fetching photos_getAllContexts for photo_id={0} (API-call! Will wait 1sec until continue)... ".format(photo_id))
    attempts = 0
    while True:
      attempts += 1
      try:
        time.sleep(1)
        result['metadata']['contexts'] = flickr_parse_json(flickrAPI.photos_getAllContexts(photo_id=photo_id, format='json'))
        break
      except Exception as e:
        print_status("\nURLError, retrying (attempt {0})... ".format(attempts))
    print "Done."

    if info['photo']['comments']['_content'] != '0':
      print_status("Fetching photos_comments_getList for photo_id={0} (API-call! Will wait 1sec until continue)... ".format(photo_id))
      attempts = 0
      while True:
        attempts += 1
        try:
          time.sleep(1)
          result['metadata']['comments'] = flickr_parse_json(flickrAPI.photos_comments_getList(photo_id=photo_id, format='json'))
          break
        except Exception as e:
          print_status("\nURLError, retrying (attempt {0})... ".format(attempts))
    else:
      result['metadata']['comments'] = []
    print "Done."

    print_status("Fetching photos_getExif for photo_id={0} (API-call! Will wait 1sec until continue)... ".format(photo_id))
    attempts = 0
    while True:
      attempts += 1
      try:
        time.sleep(1)
        result['metadata']['exif'] = flickr_parse_json(flickrAPI.photos_getExif(photo_id=photo_id, format='json'))
        break
      except Exception as e:
        print_status("\nURLError, retrying (attempt {0})... ".format(attempts))
    print "Done."

    print_status("Fetching photos_geo_getLocation for photo_id={0} (API-call! Will wait 1sec until continue)... ".format(photo_id))
    attempts = 0
    while True:
      attempts += 1
      try:
        time.sleep(1)
        result['metadata']['geo'] = flickr_parse_json(flickrAPI.photos_geo_getLocation(photo_id=photo_id, format='json'))
        break
      except Exception as e:
        print_status("\nURLError, retrying (attempt {0})... ".format(attempts))
    print "Done."

    print_status("Fetching photos_getSizes for photo_id={0} (API-call! Will wait 1sec until continue)... ".format(photo_id))
    attempts = 0
    while True:
      attempts += 1
      try:
        time.sleep(1)
        result['metadata']['sizes'] = flickr_parse_json(flickrAPI.photos_getSizes(photo_id=photo_id, format='json'))
        break
      except Exception as e:
        print_status("\nURLError, retrying (attempt {0})... ".format(attempts))
    print "Done."

    print_status("Metadata for photo {0} sucessfully crawled\n".format(photo_id))
  else:
    result['status_code'] = 403
    result['stat'] = "fail"
    result['message'] = "Photo is private"
    print_status("Photo {0} is private) cannot be crawled \n".format(photo_id))

  return result

def find_metafiles_to_process(metadata_path):
  txt_files  = glob.glob(metadata_path + '/*/*/*.txt')
  json_files = glob.glob(metadata_path + '/*/*/*[0-9].json')
  return [txt_file for txt_file in txt_files if (txt_file[:-3] + 'json') not in json_files]

def main():
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')

  api_key = config.get('Flickr API Key', 'key')
  metadata_dir = '../../' + config.get('Directories', 'metadata-dir')

  # initialize pyFlickrAPI
  pyFlickrAPI = flickrapi.FlickrAPI(api_key)

  metafiles_paths = find_metafiles_to_process(metadata_dir)
  metafiles_paths.sort()

  for metafile_path in metafiles_paths:
    print_status("Parsing file: {0}\n".format(metafile_path))
    metafile = parse_datafile(metafile_path)
    photo_id = metafile.get('Photo id')
    if url_exists(metafile.get('Web url')):
      try:
        photo_data = query_flickr(pyFlickrAPI, photo_id)
      except flickrapi.FlickrError as e:
        print_status("Cannot retrieve metadata for photo_id: {0} ({1})\n".format(photo_id,e.message))
    else:
      print_status("Photo {0} has been deleted\n".format(photo_id))
      photo_data = {"id": photo_id, "status_code": 404, "stat": "fail", "message": "Photo not found"}
    output_path = metafile_path[:-4] + '.json'
    print_status("Writing data to output file {0}... ".format(output_path))
    with open(output_path, 'w') as outfile:
      json.dump(photo_data, outfile)
    print "Done."
    print_status("Done processing photo {0} from file {1}.\n\n".format(photo_id, metafile_path))

  print_status("\n\nFinished!\n\n")

if __name__ == '__main__':
    main()
