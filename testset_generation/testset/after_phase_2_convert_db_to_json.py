#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sqlite3 as lite
import sys
import json
import random

con = None

parser = argparse.ArgumentParser(description='Frontend for the Flickr image similarity evaluation programm')
parser.add_argument('-d','--database-file', help='Path to the phase 2 DB file', required=True)
parser.add_argument('-o','--output-file', help='Path to the output file', required=True)
args = parser.parse_args()

try:
  con = lite.connect(args.database_file)

  cur = con.cursor()
  # Select all image pairs with similarities
  # If multiple users voted on same pair, select only those where all were of same oppinion
  cur.execute('''SELECT s.image_1_id, s.image_2_id, s.visual_similarity, s.semantic_similarity
                 FROM
                   semmul_image_similarity AS s,
                   (
                     SELECT image_1_id, image_2_id, COUNT(*) AS all_votes
                     FROM semmul_image_similarity
                     GROUP BY image_1_id, image_2_id
                   ) AS a,
                   (
                     SELECT image_1_id, image_2_id, COUNT(*) AS same_votes
                     FROM semmul_image_similarity
                     GROUP BY image_1_id, image_2_id, visual_similarity, semantic_similarity
                   ) AS b
                 WHERE s.image_1_id = a.image_1_id
                 AND s.image_2_id = a.image_2_id
                 AND a.image_1_id = b.image_1_id
                 AND a.image_2_id = b.image_2_id
                 AND all_votes = same_votes
                 GROUP BY s.image_1_id, s.image_2_id;''')

  # data = dict: (image_1_id, image_2_id): {visual_similarity, semantic_similarity}
  data = {(row[0], row[1]): dict(visual_similarity=row[2], semantic_similarity=row[3]) for row in cur.fetchall()}

  json.dump(data, open(args.output_file, 'w'))

  print "Wrote dict to file: %s" % args.output_file

except lite.Error, e:
  print "Error %s:" % e.args[0]
  sys.exit(1)

finally:
  if con:
    con.close()
