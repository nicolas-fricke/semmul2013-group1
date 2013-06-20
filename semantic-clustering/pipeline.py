import sys
from wordnet_searchterm_analyzer import *
sys.path.append('../helpers')
from general_helpers import load_object


def recursively_find_pictures_for_synset_tree(nodes, synsets_to_filenames_dict, find_pictures_for_hyponyms=False, find_pictures_for_meronyms=False):
  for node_name, node_values in nodes.iteritems():
    if find_pictures_for_hyponyms and node_values["hyponyms"] != None:
      node_values["hyponyms"] = recursively_find_pictures_for_synset_tree(node_values["hyponyms"], synsets_to_filenames_dict, find_pictures_for_hyponyms=True, find_pictures_for_meronyms=find_pictures_for_meronyms)
    if find_pictures_for_meronyms and node_values["meronyms"] != None:
      node_values["meronyms"] = recursively_find_pictures_for_synset_tree(node_values["meronyms"], synsets_to_filenames_dict, find_pictures_for_hyponyms=find_pictures_for_hyponyms, find_pictures_for_meronyms=True)
    node_values["picture_filenames"] = synsets_to_filenames_dict[node_name]
    #if len(node_values["picture_filenames"]) > 0:
    #  print node_values["picture_filenames"]
  return nodes

# def find_pictures_for_synset_tree(hyponyms_trees):
#   for key, value in hyponyms_trees:
#     recursively_find_pictures_for_synset_tree(value)
    

def main(argv):
  ####### Reading Commandline arguments ########
  word = parse_command_line_arguments(argv)

  ####### WordNet Search #######

  print_status("Running WordNet Search for %s... " % word)
  hyponyms_trees = find_hyponyms_on_wordnet(word)
  print "Done."

  #pretty_print_dict(hyponyms_trees)

  print_status("Done. Found %d entries.\n" % count_nested_dict(hyponyms_trees))

  synsets_to_filenames_dict = load_object("synset_filenames_dict_100.pickle")

  hyponyms_trees_with_filenames = recursively_find_pictures_for_synset_tree(hyponyms_trees, synsets_to_filenames_dict, find_pictures_for_hyponyms=True, find_pictures_for_meronyms=True)

  pretty_print_dict(hyponyms_trees_with_filenames)

if __name__ == '__main__':
  main(sys.argv[1:])