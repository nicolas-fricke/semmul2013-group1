#!/usr/bin/python
# -*- coding: utf-8 -*-

######################################################################################
#
# Search the given word in wordnet and try to cluster images which belongs to it
#
#
# authors: tino junge, nicolas fricke
# mail: {tino.junge nicolas.fricke}@student.hpi.uni-potsdam.de
######################################################################################

import sys
import getopt
from nltk.corpus import wordnet as wn
from collections import defaultdict


# Import own modules
sys.path.append('../helpers')
from general_helpers import *
from tag_preprocessing import *

def parse_command_line_arguments(argv):
  ####### Reading Commandline arguments ########

  word = ''
  try:
    opts, args = getopt.getopt(argv,"w:",["word="])
  except getopt.GetoptError:
    print 'wordnet_searchterm_analyzer.py -w <word>'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-w':
      word = arg
    else:
      print 'wordnet_searchterm_analyzer.py -w <word>'
      sys.exit()

  if word == '':
    print 'Error1: parameter word cannot be blank'
    print 'Syntax: wordnet_searchterm_analyzer.py -w <word>'
    sys.exit()

  return word

def recursively_find_all_hyponyms_on_wordnet(synset_name):
  synset = wn.synset(synset_name)
  hyponyms = synset.hyponyms()
  if len(hyponyms) == 0:
    return None
  else:
    hyponyms_of_synset = {}
    for hyponym in hyponyms:
      hyponyms_of_synset[hyponym.name] = {
        "hyponyms": recursively_find_all_hyponyms_on_wordnet(hyponym.name),
        "meronyms": recursively_find_all_meronyms_on_wordnet(hyponym.name)
      }
    return hyponyms_of_synset

def recursively_find_all_meronyms_on_wordnet(synset_name):
  synset = wn.synset(synset_name)
  meronyms = synset.part_meronyms()
  if len(meronyms) == 0:
    return None
  else:
    meronyms_of_synset = {}
    for meronym in meronyms:
      meronyms_of_synset[meronym.name] = {
        "hyponyms": recursively_find_all_hyponyms_on_wordnet(meronym.name),
        "meronyms": recursively_find_all_meronyms_on_wordnet(meronym.name)
      }
    return meronyms_of_synset

def find_hyponyms_on_wordnet(word):
  hyponym_tree = {}
  for synset in wn.synsets(word):
    hyponym_tree[synset.name] = {
      "hyponyms": recursively_find_all_hyponyms_on_wordnet(synset.name),
      "meronyms": recursively_find_all_meronyms_on_wordnet(synset.name)
    }
  return hyponym_tree

def pretty_print_dict(d, indent=0):
   parent_indent = indent - 1 if indent > 0 else 0
   if not isinstance(d, dict): return
   for key, value in d.iteritems():
      print '|   ' * parent_indent + ('|-- ' if indent > 0 else "")  + str(key)
      if isinstance(value, dict):
         pretty_print_dict(value, indent + 1)

def count_nested_dict(d):
  counter = 0
  for value in d.values():
    counter += 1
    if value != None:
      counter += count_nested_dict(value)
  return counter

def main(argv):
  ####### Reading Commandline arguments ########
  word = parse_command_line_arguments(argv)

  ####### WordNet Search #######

  print_status("Running WordNet Search for %s... " % word)
  hyponyms_trees = find_hyponyms_on_wordnet(word)
  print "Done."

  pretty_print_dict(hyponyms_trees)

  print_status("Done. Found %d entries.\n" % count_nested_dict(hyponyms_trees))


if __name__ == '__main__':
  main(sys.argv[1:])
