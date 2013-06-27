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

import ConfigParser
import sys
import getopt
from nltk.corpus import wordnet as wn
from collections import defaultdict
from json import *

# Import own modules
from helpers.general_helpers import *
from clustering.semantic.tag_preprocessing import *

class WordnetNode:
  def __init__(self, name, hyponyms, meronyms, strong_cooccurrences=None):
    self.name = name
    self.strong_cooccurrences = strong_cooccurrences if isinstance(strong_cooccurrences, list) else [] 
    self.hyponyms = hyponyms if isinstance(hyponyms, list) else []
    self.meronyms = meronyms if isinstance(meronyms, list) else []
    self.associated_pictures = None
    self.subclusters = None

  def has_hyponyms(self):
    return isinstance(self.hyponyms, list) and len(self.hyponyms) > 0

  def has_meronyms(self):
    return isinstance(self.meronyms, list) and len(self.meronyms) > 0

  def has_child_nodes(self):
    return self.has_hyponyms() or self.has_meronyms()

  def has_pictures(self):
    return isinstance(self.associated_pictures, list) and len(self.associated_pictures) > 0

class WordnetNodeJSONEncoder(JSONEncoder):
  def default(self, o):
    return o.__dict__

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

def find_strong_co_occurrences(synset_name, synset_tag_tf_idf_dict_filename):
  tags_with_strong_co_occurrence = []
  synset_tag_tf_idf_dict = load_object(synset_tag_tf_idf_dict_filename)
  
  return tags_with_strong_co_occurrence

def recursively_find_all_hyponyms_on_wordnet(synset_name):
  synset = wn.synset(synset_name)
  hyponyms = synset.hyponyms()
  if len(hyponyms) == 0:
    return None
  else:
    hyponyms_of_synset = []
    for hyponym in hyponyms:
      hyponyms_of_synset.append(WordnetNode(
        name = hyponym.name,
        hyponyms = recursively_find_all_hyponyms_on_wordnet(hyponym.name),
        meronyms = recursively_find_all_meronyms_on_wordnet(hyponym.name)
      ))
    return hyponyms_of_synset

def recursively_find_all_meronyms_on_wordnet(synset_name):
  synset = wn.synset(synset_name)
  meronyms = synset.part_meronyms()
  if len(meronyms) == 0:
    return None
  else:
    meronyms_of_synset = []
    for meronym in meronyms:
      meronyms_of_synset.append(WordnetNode(
        name = meronym.name,
        hyponyms = recursively_find_all_hyponyms_on_wordnet(meronym.name),
        meronyms = recursively_find_all_meronyms_on_wordnet(meronym.name)
      ))
    return meronyms_of_synset

def find_hyponyms_on_wordnet(word):
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  synset_tag_tf_idf_dict_filename = config.get('Filenames for Pickles', 'synset-tag-cooccurrence-dict')

  # build tree
  hyponym_tree = []
  for synset in wn.synsets(word):
    hyponym_tree.append(WordnetNode(
      name = synset.name,
      hyponyms = recursively_find_all_hyponyms_on_wordnet(synset.name),
      meronyms = recursively_find_all_meronyms_on_wordnet(synset.name),
      strong_cooccurrences = find_strong_co_occurrences(synset.name, synset_tag_tf_idf_dict_filename)
    ))
  return hyponym_tree

def pretty_print_tree(tree_node, indent=0):
   parent_indent = indent - 1 if indent > 0 else 0
   print '|   ' * parent_indent + ('|-- ' if indent > 0 else "")  + tree_node.name
   if tree_node.has_pictures():
     print '|   ' * indent + '| '  + "%d photos associated" % len(tree_node.associated_pictures)
   if tree_node.has_hyponyms():
     print '|   ' * indent + '| '  + "hyponyms:"
     for child_hyponym_node in tree_node.hyponyms:
       pretty_print_tree(child_hyponym_node, indent + 1)
   if tree_node.has_meronyms():
     print '|   ' * indent + '| '  + "meronyms:"
     for child_meronym_node in tree_node.meronyms:
       pretty_print_tree(child_meronym_node, indent + 1)

def recursively_count_tree_nodes(tree_node):
  counter = 0
  if tree_node.has_hyponyms():
    for child_hyponym_node in tree_node.hyponyms:
      counter += recursively_count_tree_nodes(child_hyponym_node)
  if tree_node.has_meronyms():
    for child_meronym_node in tree_node.meronyms:
      counter += recursively_count_tree_nodes(child_meronym_node)
  return counter

def count_tree_nodes(wordnet_node_list):
  counter = 0
  for node in wordnet_node_list:
    counter += recursively_count_tree_nodes(node)
  return counter

def main(argv):
	####### Reading Commandline arguments ########
	word = parse_command_line_arguments(argv)

	####### WordNet Search #######

	print_status("Running WordNet Search for %s... " % word)
	hyponyms_trees = find_hyponyms_on_wordnet(word)
	print "Done."

	for synset in hyponyms_trees:
		pretty_print_tree(synset)

	print_status("Done. Found %d entries.\n" % count_tree_nodes(hyponyms_trees))

if __name__ == '__main__':
	main(sys.argv[1:])
