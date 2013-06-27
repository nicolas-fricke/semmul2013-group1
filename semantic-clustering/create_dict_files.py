#!/usr/bin/python
# -*- coding: utf-8 -*-

#########################################################################################
# Create picture and synset/tag dictionaries and write them on disk
#
# filename -> list(synsets) list(tags) url
# synset -> list(filename,url)
# tag -> list(filename,url)
# synset -> list(tag,tf_idf)
#
# authors: tino junge, claudia exeler, mandy roick
# mail: tino.junge@student.hpi.uni-potsdam.de, claudia.exeler@student.hpi.uni-potsdam.de, 
#       mandy.roick@student.hpi.uni-potsdam.de
#########################################################################################

from collections import defaultdict

# Import own modules
import sys
sys.path.append('../helpers')
from general_helpers import *

from semantic_clustering import *
from synset_detection import *


def main():
  number_of_jsons = 100

  print_status("Detecting synsets for the tags of every picture... \n")
  _, storable_keywords_for_pictures = synset_detection(number_of_jsons)
  print_status("Done detecting synsets \n")

  print_status("Writing keywords_for_pictures... ")
  save_object(storable_keywords_for_pictures,"keywords_for_pictures.pickle")
  print "Done."

  print_status("Create_inverse_keywords_for_pictures_dicts... ")
  storable_synset_filenames_dict, unmatched_tag_filenames_dict = create_inverse_keywords_for_pictures_dict(storable_keywords_for_pictures)
  print "Done"

  print_status("Writing synset_filenames_dict... ")
  save_object(storable_synset_filenames_dict,"synset_filenames_dict.pickle")
  print "Done."

  print_status("Writing unmatched_tag_filenames_dict... ")
  save_object(unmatched_tag_filenames_dict,"unmatched_tag_filenames_dict.pickle")
  print "Done."

  print_status("Create tf_idf dictionary... ")
  storable_synset_unmatched_tags_tf_idfs_dict = create_unmatched_tag_tf_idf_dict(storable_synset_filenames_dict, 
                                                                                 unmatched_tag_filenames_dict)
  print "Done"

  print_status("Writing storable_synset_unmatched_tags_tf_idfs_dict... ")
  save_object(storable_synset_unmatched_tags_tf_idfs_dict,"storable_synset_unmatched_tags_tf_idfs_dict.pickle")
  print "Done."

if __name__ == '__main__':
    main()