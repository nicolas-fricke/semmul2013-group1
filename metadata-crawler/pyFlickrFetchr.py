#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# Script crawls available metadata from Flickr for given Flickr photo_id.
# Flickr API key file expected in given text file:
#     <api_key>\n
#     <secret>
# i.e. API key in first line, secret in second line.
#
#   ##################################################
#   #                                                #
#   #  Update: uses same config file as crawler.py!  #
#   #      No need to copy keys into new file.       #
#   #                                                #
#   #                                       -- nico  #
#   ##################################################
#
# author: christian hentschel
# mail: christian.hentschel@hpi.uni-potsdam.de
################################################################################


import flickrapi
import sys
import time
import pprint
import ConfigParser

def print_usage():
	print "Usage pyFlickrFetchrMeta.py <flickr_photo_id>"


def load_api_key():
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  api_key = config.get('Flickr API Key', 'key')
  secret  = config.get('Flickr API Key', 'secret')
  return (api_key,secret)

def fetch_photo_metadata(flickr,photo_id):
	metadata={}

	print "Fetching metadata for photo_id={0} (API-call! Will wait 1sec until continue)...".format(photo_id),
	time.sleep(1)
	info = flickr.photos_getInfo(photo_id=photo_id)

	#id
	metadata['photo_id'] = int(photo_id)

	#title
	if info.find('photo').find('title').text is None:
		metadata['title'] 	= ""
	else:
		metadata['title'] 	= info.find('photo').find('title').text.strip()

	#description
	if info.find('photo').find('description').text is None:
		metadata['description'] = None
	else:
		metadata['description'] = info.find('photo').find('description').text.strip()

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
	if len(sys.argv) != 2:
		print_usage()
		sys.exit(-1)


	#load flickr api key
	api_key, secret = load_api_key()

	photo_id = int(sys.argv[1])

	flickr = flickrapi.FlickrAPI(api_key)

	print "Asking Flickr for photo metadata for id='{0}'...".format(photo_id)


	try:
		photo_meta_data = fetch_photo_metadata(flickr,photo_id)
		print "Found the following metedata:\n___________________________________________________________________________\n\n"
		pp = pprint.PrettyPrinter(indent=3)
		pp.pprint(photo_meta_data)
	except flickrapi.FlickrError as e:
		print "Cannot retrieve metadata for photo_id: {0} ({1})".format(photo_id,e.message)
	print "\n\nFinished: ",time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())

if __name__=='__main__':
    main()

