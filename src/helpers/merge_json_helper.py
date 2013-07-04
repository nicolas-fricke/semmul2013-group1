import ConfigParser
from helpers.general_helpers import find_metajsons_to_process_in_dir, parse_json_file, import_metadata_dir_of_config, write_json_file

def main():
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  visual_data_dir = config.get('Directories', 'visual-data-dir')
  visual_features_filename = config.get('Filenames for Pickles', 'visual_features_filename')
  visual_features_filename = visual_features_filename.replace("##","all")

  # combine all visual jsons in path to one json
  monster_json = {}
  for json_file in find_metajsons_to_process_in_dir(visual_data_dir):
    monster_json.update(parse_json_file(json_file))

  write_json_file(monster_json,visual_features_filename)

if __name__ == '__main__':
  main()