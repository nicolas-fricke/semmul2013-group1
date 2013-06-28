from glob import glob
import json
import sys
import time
import os
import cPickle as pickle

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
  return glob(metadata_path + '/*/*/*.json')

def parse_json_file(json_file):
  with open(json_file) as file:
    return json.load(file)

def construct_path_to_json(metajson):
  parent_folder_name = metajson[:2]
  grand_parent_folder_name = parent_folder_name[:1]+"0-"+parent_folder_name[:1]+"9"
  return "/"+grand_parent_folder_name+"/"+parent_folder_name+"/"+metajson

def get_small_image_url(metajson):
  if not metajson.get("stat") == "ok":
    return None
  sizes = metajson["metadata"]["sizes"]
  if not sizes.get("stat") == "ok":
    return None
  return [entry["source"] for entry in sizes["sizes"]["size"] if entry["label"] == "Small"][0]

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