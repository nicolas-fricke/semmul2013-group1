#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sqlite3 as lite
import sys
import json
import random

con = None

parser = argparse.ArgumentParser(description='Frontend for the Flickr image similarity evaluation programm')
parser.add_argument('-t','--testset-file', help='Path to the testset JSON file', required=True)
parser.add_argument('-d','--database-file', help='Path to the phase 1 DB file', required=True)
parser.add_argument('-s','--testset-size', help='How many images shall be included in the testset. Images are selected randomly', type=int, required=True)
parser.add_argument('-o','--output-file', help='Path to the output file', required=True)
args = parser.parse_args()

try:
  con = lite.connect(args.database_file)

  cur = con.cursor()
  cur.execute('''SELECT image_id, count(*) as votes, sum(contains_food) as positive_votes
                 FROM semmul_images
                 GROUP BY image_id
                 HAVING votes - positive_votes < 0.5 * votes
                 ORDER BY votes DESC;''')

  data = [dict(image_id=row[0], votes=row[1], positive_votes=row[2]) for row in cur.fetchall()]

  j = json.load(open(args.testset_file, 'r'))

  food_dict = {}

  for x in range(0, len(data)):
    food_dict[str(data[x]['image_id'])] = j[str(data[x]['image_id'])]
    # print "id: %5d votes: %3d positives: %3d" % (data[x]['image_id'], data[x]['votes'], data[x]['positive_votes'])

  print "Total: %d images" % len(data)

  image_selection = dict([(key, j[key]) for key in random.sample(j, args.testset_size)])

  print "Selected %d images at random" % len(image_selection)

  json.dump(food_dict, open(args.output_file, 'w'))

  print "Wrote new testset to file: %s" % args.output_file

except lite.Error, e:
  print "Error %s:" % e.args[0]
  sys.exit(1)

finally:
  if con:
    con.close()
