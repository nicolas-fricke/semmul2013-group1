import sys
from clustering.semantic.wordnet_searchterm_analyzer import *
from clustering.visual.combined_clustering import *
from clustering.semantic.mcl_keyword_clustering import cluster_via_mcl
from helpers.general_helpers import load_object

################ finding pictures for Wordnet Nodes #######################
def find_associated_pictures(node, synsets_to_filenames_dict, tags_to_filenames_dict):
  associated_pictures = []
  if node.name in synsets_to_filenames_dict:
    associated_pictures.extend(synsets_to_filenames_dict[node.name])
  if len(associated_pictures) > 0:
    print "before: ", len(associated_pictures)
  for tag in node.co_occurring_tags:
    for picture in tags_to_filenames_dict[tag]:
      if picture not in associated_pictures:
        associated_pictures.append(picture)
  if len(associated_pictures) > 0:
    print "after: ", len(associated_pictures)
  return associated_pictures

def recursively_find_pictures_for_synset_tree(nodes, synsets_to_filenames_dict, find_pictures_for_hyponyms=False, find_pictures_for_meronyms=False, find_pictures_for_tags=False, tags_to_filenames_dict={}):
  for node in nodes:
    if find_pictures_for_hyponyms and node.has_hyponyms():
      recursively_find_pictures_for_synset_tree(node.hyponyms, synsets_to_filenames_dict, find_pictures_for_hyponyms=True, find_pictures_for_meronyms=find_pictures_for_meronyms)
    if find_pictures_for_meronyms and node.has_meronyms():
      recursively_find_pictures_for_synset_tree(node.meronyms, synsets_to_filenames_dict, find_pictures_for_hyponyms=find_pictures_for_hyponyms, find_pictures_for_meronyms=True)
    node.associated_pictures = find_associated_pictures(node, synsets_to_filenames_dict, tags_to_filenames_dict)
    #print node.name, " has %d associated_pictures." % len(node.associated_pictures)
  return nodes

# def find_pictures_for_synset_tree(hyponyms_trees, synsets_to_filenames_dict, find_pictures_for_hyponyms=True, find_pictures_for_meronyms=True):
#   for node in hyponyms_trees:
#     recursively_find_pictures_for_synset_tree(node, synsets_to_filenames_dict, find_pictures_for_hyponyms=find_pictures_for_hyponyms, find_pictures_for_meronyms=find_pictures_for_meronyms)
#   return hyponyms_trees

def get_searchtrees_with_filenames(search_term):
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  synset_filenames_dict_filename = config.get('Filenames for Pickles', 'synset_filenames_dict_filename')
  tag_filenames_dict_filename = config.get('Filenames for Pickles', 'unmatched_tag_filenames_dict_filename')
  synset_tag_tf_idf_dict_filename = config.get('Filenames for Pickles', 'synset-tag-cooccurrence-dict')

  ####### WordNet Search #######
  tf_idf_tuple = load_object(synset_tag_tf_idf_dict_filename)

  print_status("Running WordNet Search for %s... " % search_term)
  hyponyms_trees = find_hyponyms_on_wordnet(search_term, tf_idf_tuple)
  print "Done."

  #pretty_print_tree(hyponyms_trees)

  print_status("Found %d entries.\n" % count_tree_nodes(hyponyms_trees))

  synsets_to_filenames_dict = load_object(synset_filenames_dict_filename)
  tags_to_filenames_dict = load_object(tag_filenames_dict_filename)

  searchtrees_with_pictures = recursively_find_pictures_for_synset_tree(hyponyms_trees, synsets_to_filenames_dict, find_pictures_for_hyponyms=True, find_pictures_for_meronyms=True, tags_to_filenames_dict=tags_to_filenames_dict)

  return searchtrees_with_pictures

def get_clusters(search_term):
  searchtrees_with_pictures = get_searchtrees_with_filenames(search_term)

  result_trees = []
  for searchtree in searchtrees_with_pictures:
    print_status("Assign pictures to most fitting keyword cluster.... ")
    mcl_clustered_searchtree = cluster_via_mcl(searchtree)
    print "Done.\n"
    result_trees.append(cluster_visually(mcl_clustered_searchtree))

  return result_trees

def main(argv):
  ####### Reading Commandline arguments ########
  word = parse_command_line_arguments(argv)

  ####### Creating hyponym_trees ###########
  hyponyms_trees_with_filenames = get_searchtrees_with_filenames(word)

  for synset in hyponyms_trees_with_filenames:
    pretty_print_tree(synset)

if __name__ == '__main__':
  main(sys.argv[1:])