from glob import glob
import json
import sys
import time
import os
import os.path
import cPickle as pickle
import ConfigParser


def print_status(message):
  sys.stdout.write(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + " - ")
  sys.stdout.write(message)
  sys.stdout.flush()

def tag_is_present(tag_content, tag_list):
  for tag in tag_list:
    if tag["_content"] == tag_content:
      return True
  return False

def save_object(obj, filename):
  with open(filename, 'wb') as output:
      pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

def load_object(filename):
  with open(filename, 'rb') as input:
      return pickle.load(input)

def find_metajsons_to_process(metadata_path):
  return find_metajsons_to_process_in_dir(metadata_path + '/*/*')

def find_metajsons_to_process_in_dir(metatdata_dir):
  return glob(metatdata_dir + '/*.json')

def write_json_file(obj, filename):
  with open(filename, 'wb') as output:
    output.write(json.dumps(obj))

def parse_json_file(json_file):
  with open(json_file) as file:
    try:
      return json.load(file)
    except ValueError:
      return None

def construct_path_to_json(metajson):
  parent_folder_name = metajson[:2]
  grand_parent_folder_name = parent_folder_name[:1]+"0-"+parent_folder_name[:1]+"9"
  return os.sep+grand_parent_folder_name+os.sep+parent_folder_name+os.sep+metajson

def get_small_image_url(metajson):
  if not metajson.get("stat") == "ok":
    return None
  sizes = metajson["metadata"]["sizes"]
  if not sizes.get("stat") == "ok":
    return None

  small_image_urls = [entry["source"] for entry in sizes["sizes"]["size"] if entry["label"] == "Small"]
  if len(small_image_urls) == 0:
    return None
  return small_image_urls[0]

def write_clusters_to_html(clusters, html_file_path="out.html", additional_columns=None, open_in_browser=False):
  output_html =  ( "<html>\n"
                   "  <head>\n"
                   "    <title>Cluster Visualization</title>\n"
                   "    <style>\n"
                   "      table {width: 100%; table-layout: fixed; border-collapse: collapse;}\n"
                   "      tr > td:first-child {text-align: center; font-weight: bold;}"
                   "      td {border: 2px solid black; margin: 5px;}\n"
                   "      .images {white-space: nowrap; overflow: scroll;}\n"
                   "    </style>\n"
                   "  </head>\n"
                   "  <body>\n"
                   "    <table border='1'>\n"
                   "      <tr>\n"
                   "        <th style='width: 100px'>Cluster</th>\n")
  if additional_columns != None:
    for column_heading in additional_columns.keys():
      output_html+="        <th style='width: 300px'>%s</th>\n" % column_heading
  output_html+=  ( "        <th>Images</th>\n"
                   "      </tr>\n")
  for cluster_number, images in clusters.iteritems():
    output_html +=("      <tr>\n"
                   "        <td>#%d<br/><i>(%d images)</i></td>\n" % (cluster_number, len(images)))
    if additional_columns != None:
      for column in additional_columns.values():
        output_html += "        <td>%s</td>\n" % column[cluster_number]
    output_html += "        <td class='images'>\n"
    for image in images:
      output_html+="        <img src='%s'" % image["url"]
      if image.get("score") != None:
        output_html += "title='Score:%f'" % image["score"]
      output_html += "/>\n"
    output_html += "        </td></tr>\n"
  output_html += ( "    </table>\n"
                   "  </body>\n"
                   "</html>")
  with open(html_file_path, "w") as output_file:
    output_file.write(output_html)
  if open_in_browser:
    try:
      os.system("open -a Google\ Chrome " + html_file_path)
    except BaseException:
      return

def read_clusters_from_file(file_name):
  cluster_for_synsets = dict()
  cluster_file = open(file_name, 'r')
  for number_of_cluster, line in enumerate(cluster_file):
    for synset in line.rstrip('\n\r').split('\t'):
      cluster_for_synsets[synset] = number_of_cluster
  cluster_file.close()
  return cluster_for_synsets

def read_cluster_representatives(file_name):
  clusters = [""]
  cluster_file = open(file_name, 'r')
  for number_of_cluster, line in enumerate(cluster_file):
    representatives = line.rstrip('\n\r').split('\t')
    #if len(representatives) > 5:
    #  representatives = representatives[:4]
    clusters.append(representatives)
  return clusters

############ Config Import Methods #############

def import_metadata_dir_of_config(path):
  config = ConfigParser.SafeConfigParser()
  config.read(path)
  return config.get('Directories', 'metadata-dir')

def get_name_from_config(section, name):
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')
  return config.get(section, name)

############ Feature Loading Methods #############

def load_visual_features():
  visual_features_filename = get_name_from_config('Filenames for Pickles', 'visual_features_filename')
  visual_features_filename = visual_features_filename.replace('##', 'all')
  visual_features = parse_json_file(visual_features_filename)
  if visual_features == None:
    print "Could not read visual_features file %s" % visual_features_filename
    return {}
  return visual_features

def load_cluster_for_synsets():
  mcl_filename = get_name_from_config('Filenames for Pickles', 'mcl_clusters_filename')
  cluster_for_synsets = read_clusters_from_file(mcl_filename)
  return cluster_for_synsets

def load_keywords_for_pictures():
  keywords_for_pictures_filename = get_name_from_config('Filenames for Pickles', 'keywords_for_pictures_filename')
  keywords_for_pictures_filename = keywords_for_pictures_filename.replace('##', 'all')
  keywords_for_pictures = parse_json_file(keywords_for_pictures_filename)
  return keywords_for_pictures

def load_synset_filenames_dict():
  synset_filenames_dict_filename = get_name_from_config('Filenames for Pickles', 'synset_filenames_dict_filename')
  filenames_for_synsets = parse_json_file(synset_filenames_dict_filename)
  return filenames_for_synsets



