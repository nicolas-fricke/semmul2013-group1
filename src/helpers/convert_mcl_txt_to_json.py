#!/usr/bin/python
# -*- coding: utf-8 -*-

######################################################################################
#
# Convert a given pickle into a json file if possible
#
#
# authors: Mandy Roick
# mail: mandy.roick@student.hpi.uni-potsdam.de
######################################################################################

from clustering.semantic.mcl_keyword_clustering import sorted_cluster_representatives
from helpers.general_helpers import load_synset_filenames_dict

def main():
  filenames_for_synsets = load_synset_filenames_dict()
  sorted_cluster_representatives(filenames_for_synsets)

if __name__ == '__main__':
    main()