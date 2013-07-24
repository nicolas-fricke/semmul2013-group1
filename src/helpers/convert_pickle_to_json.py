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

import argparse
from helpers.general_helpers import *

def parse_command_line_arguments():
  parser = argparse.ArgumentParser(description='ADD DESCRIPTION TEXT.')
  parser.add_argument('-p','--path-to-pickle', dest='path_to_pickle', type=str,
                      help='Specifies where to find the pickle which has to be converted')
  args = parser.parse_args()
  return args

def main(argv):
  arguments = parse_command_line_arguments()
  pickle_object = load_object(arguments.path_to_pickle)
  write_json_file(pickle_object, arguments.path_to_pickle.replace(".pickle", ".json"))

if __name__ == '__main__':
    main(sys.argv[1:])