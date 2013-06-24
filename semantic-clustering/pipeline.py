import sys
from wordnet_searchterm_analyzer import *
sys.path.append('../helpers')
from general_helpers import load_object


def recursively_find_pictures_for_synset_tree(nodes, synsets_to_filenames_dict, find_pictures_for_hyponyms=False, find_pictures_for_meronyms=False):
  for node in nodes:
    if find_pictures_for_hyponyms and node.has_hyponyms():
      print node.hyponyms
      recursively_find_pictures_for_synset_tree(node.hyponyms, synsets_to_filenames_dict, find_pictures_for_hyponyms=True, find_pictures_for_meronyms=find_pictures_for_meronyms)
    if find_pictures_for_meronyms and node.has_meronyms():
      recursively_find_pictures_for_synset_tree(node.meronyms, synsets_to_filenames_dict, find_pictures_for_hyponyms=find_pictures_for_hyponyms, find_pictures_for_meronyms=True)
    node.associated_pictures = synsets_to_filenames_dict[node.name]
  return nodes

# def find_pictures_for_synset_tree(hyponyms_trees, synsets_to_filenames_dict, find_pictures_for_hyponyms=True, find_pictures_for_meronyms=True):
#   for node in hyponyms_trees:
#     recursively_find_pictures_for_synset_tree(node, synsets_to_filenames_dict, find_pictures_for_hyponyms=find_pictures_for_hyponyms, find_pictures_for_meronyms=find_pictures_for_meronyms)
#   return hyponyms_trees

def get_hyponyms_trees_with_filenames(search_term):
  ####### WordNet Search #######

  print_status("Running WordNet Search for %s... " % search_term)
  hyponyms_trees = find_hyponyms_on_wordnet(search_term)
  print "Done."

  #pretty_print_tree(hyponyms_trees)

  print_status("Done. Found %d entries.\n" % count_tree_nodes(hyponyms_trees))

  synsets_to_filenames_dict = load_object("../semantic-clustering/synset_picture_urls_dict_5000.pickle")

  hyponyms_trees_with_filenames = recursively_find_pictures_for_synset_tree(hyponyms_trees, synsets_to_filenames_dict, find_pictures_for_hyponyms=True, find_pictures_for_meronyms=True)

  return hyponyms_trees_with_filenames

def main(argv):
  ####### Reading Commandline arguments ########
  word = parse_command_line_arguments(argv)

  ####### Creating hyponym_trees ###########
  hyponyms_trees_with_filenames = get_hyponyms_trees_with_filenames(word)

  for synset in hyponyms_trees_with_filenames:
    pretty_print_tree(synset)

if __name__ == '__main__':
  main(sys.argv[1:])