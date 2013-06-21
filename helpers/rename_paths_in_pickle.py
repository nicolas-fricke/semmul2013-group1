from collections import defaultdict
import sys
sys.path.append('../helpers')
from general_helpers import *

def main():
  synset_filenames_dict = load_object("synset_filenames_dict_5000.pickle")
  new_synset_filenames_dict = defaultdict(list)
  for synset, filename_list in synset_filenames_dict.iteritems():
    new_synset_filenames_dict[synset] = []
    for filename in filename_list:
      new_synset_filenames_dict[synset].append(filename.replace("../files_to_be_calculated","data/metadata"))
  save_object(new_synset_filenames_dict,"own_synset_filenames_dict_5000.pickle")

if __name__ == '__main__':
  main()