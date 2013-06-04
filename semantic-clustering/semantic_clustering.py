#!/usr/bin/python
# -*- coding: utf-8 -*-

######################################################################################
# Clusters the given images semantically
#
#
# authors: tino junge, mandy roick
# mail: tino.junge@student.hpi.uni-potsdam.de, mandy.roick@student.hpi.uni-potsdam.de
######################################################################################

from collections import defaultdict
import operator

# Import own modules
from tag_preprocessing import *
from tag_clustering import *


################     Photo Clustering  #############################

def intersect_tag_lists(tag_cluster,tag_list):
  return list(set(tag_cluster).intersection( set(tag_list) ))


def get_photo_clusters(tag_clusters,photo_tags_dict):
  affiliated_photos_tuples = []
  for tag_cluster in tag_clusters:
    affiliated_photos = {}
    for photo_id, tag_list in photo_tags_dict.items():
      if (not tag_list == None) and (len(tag_list) > 0):
        shared_tags = intersect_tag_lists(tag_cluster,tag_list)
        #print "Photo %d | shared tags = %d | shared_tags / photo_tags = %f | shared_tags / tag_cluster = %f" % (photo_id,len(shared_tags),len(shared_tags)/float(len(tag_list)),len(shared_tags)/float(len(tag_cluster)))
        if len(shared_tags) > 0:
          affiliation_score = len(shared_tags)/float(len(tag_list)) + len(shared_tags)/float(len(tag_cluster))
          affiliated_photos[photo_id] = affiliation_score
    sorted_affiliated_photos = sorted(affiliated_photos.iteritems(), key=operator.itemgetter(1))
    sorted_affiliated_photos.reverse()
    affiliated_photos_tuples.append(sorted_affiliated_photos)
    #print sorted_affiliated_photos
  return affiliated_photos_tuples


################     Main        ###################################

def main():
  number_of_jsons = 100

  tag_co_occurrence_histogram, tag_index_dict, photo_tags_dict, photo_data_list = tag_preprocessing(number_of_jsons);

  tag_clusters = tag_clustering(tag_index_dict, tag_co_occurrence_histogram)

  # cluster photos
  print "Calculate photo clusters"
  photo_clusters = get_photo_clusters(tag_clusters,photo_tags_dict)
  print "Done"

  # write clusters to html
  clusters = defaultdict(list)
  additional_columns= {}
  additional_columns["Tags"] = []
  for index, cluster in enumerate(photo_clusters):
    additional_columns["Tags"].append(tag_clusters[index])
    for photo_id, score in cluster:
      clusters[index].append(dict(photo_data_list[photo_id].items()+{"score":score}.items()))

  name_of_html_file = str(number_of_jsons) + "_old_q_second_smallest.html"
  write_clusters_to_html(clusters, html_file_path=name_of_html_file, additional_columns=additional_columns, open_in_browser=True)

if __name__ == '__main__':
    main()
