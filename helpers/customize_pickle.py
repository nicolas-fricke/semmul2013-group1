from collections import defaultdict
import sys
sys.path.append('../helpers')
from general_helpers import *

def get_image_url_for_filename(filename):
  metadata = parse_json_file(filename)
  return get_small_image_url(metadata)

def change_path(filename):
  return filename.replace("../files_to_be_calculated","data/metadata")

def main():
  synset_filenames_dict = load_object("../frontend/own_synset_filenames_dict_5000.pickle")
  new_synset_filenames_dict = defaultdict(list)
  for synset, filename_list in synset_filenames_dict.iteritems():
    new_synset_filenames_dict[synset] = []
    for filename in filename_list:
      new_synset_filenames_dict[synset].append(get_image_url_for_filename(filename))
  save_object(new_synset_filenames_dict,"../frontend/new_synset_filenames_dict_5000.pickle")

if __name__ == '__main__':
  main()