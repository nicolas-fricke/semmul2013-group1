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
from subprocess import call
import argparse
from nltk.corpus import wordnet as wn

# Import own modules
from tag_preprocessing import *
from tag_clustering import *
from synset_detection import synset_detection

################     Write to File    ##############################

def write_tag_similarity_histogram_to_file(tag_similarity_histogram, file_name):
  print "Writing similarity file."
  output_file = open(file_name, 'w')
  for (synset1, synset2), similarity in tag_similarity_histogram.iteritems():
    output_file.write(str(synset1) + ' ' + str(synset2) + ' ' + str(similarity) + '\n')
    #output_file.write(tag2 + ' ' + tag1 + ' ' + str(similarity) + '\n')
  output_file.close()

################     Similarity Historgram   #######################

def calculate_similarity_histogram(keywords_for_pictures):
  synset_filenames_dict = defaultdict(list)
  for filename, (_, synset_list) in keywords_for_pictures.iteritems():
    for synset in synset_list:
      synset_filenames_dict[synset].append(filename)

  similarity_histogram = dict()
  for synset1, filenames1 in synset_filenames_dict.iteritems():
    #print synset1.name()
    for synset2, filenames2 in synset_filenames_dict.iteritems():
      if synset1 < synset2:
        if (synset1, synset2) not in similarity_histogram:
          co_occurrence = len(set(filenames1).intersection(set(filenames2)))
          print synset2.lch_similarity(synset1)
          similarity_histogram[(synset1, synset2)] = synset1.lch_similarity(synset2) * co_occurrence
    #for filename in filenames:
  return similarity_histogram


################     MCL Clustering    #############################

def read_clusters_from_file(file_name):
  clusters = []
  cluster_file = open(file_name, 'r')
  for line in cluster_file:
    clusters.append(line.rstrip('\n\r').split('\t'))
  cluster_file.close()
  return clusters

def mcl_tag_clustering(tag_histogram):
  histogram_file_name = 'tag_similarity_file2.txt'
  write_tag_similarity_histogram_to_file(tag_histogram, histogram_file_name)
  out_file_name = "out.txt"
  call(["mcl", histogram_file_name, "--abc", "-o", out_file_name])
  #call("mcl " + histogram_file_name + " --abc -o " + out_file_name, shell=True)
  return read_clusters_from_file(out_file_name)

################     Photo Clustering  #############################

def intersect_keyword_lists(keyword_cluster,keyword_list):
  return list(set(keyword_cluster).intersection( set(keyword_list) ))


def get_photo_clusters(keyword_clusters, keywords_for_pictures):
  affiliated_photos_tuples = []
  for keyword_cluster in keyword_clusters:
    affiliated_photos = {}
    for photo_url, keyword_list in keywords_for_pictures.iteritems():
      if (not keyword_list == None) and (len(keyword_list) > 0):
        shared_keywords = intersect_keyword_lists(keyword_cluster,keyword_list)
        #print "Photo %d | shared keywords = %d | shared_keywords / photo_keywords = %f | shared_keywords / keyword_cluster = %f" % (photo_id,len(shared_keywords),len(shared_keywords)/float(len(keyword_list)),len(shared_keywords)/float(len(keyword_cluster)))
        if len(shared_keywords) > 0:
          affiliation_score = len(shared_keywords)/float(len(keyword_list)) + len(shared_keywords)/float(len(keyword_cluster))
          affiliated_photos[photo_url] = affiliation_score
    sorted_affiliated_photos = sorted(affiliated_photos.iteritems(), key=operator.itemgetter(1))
    sorted_affiliated_photos.reverse()
    affiliated_photos_tuples.append(sorted_affiliated_photos)
    #print sorted_affiliated_photos
  return affiliated_photos_tuples


################     Main        ###################################

# cut off lowest 10% of synsets
# save filename of pictures in pickle, datastructure keyword_for_picture should be: {json_file_name: (url, [synsets]), ...}
# calculation of keyword_similarity_histogram (probably synset similarities combined with co_occurrences)
# adapt get_photo_clusters and photo_clusters according to have file name in keywords_for_pictures

def main():
  number_of_jsons = 100

  parser = argparse.ArgumentParser()
  parser.add_argument('-p','--preprocessed', dest='use_preprocessed_data', action='store_true',
                      help='If specified, use preprocessed keyword data, otherwise find keywords and save values to file for next use')
  args = parser.parse_args()

  print_status("Use preprocessed data: " + str(args.use_preprocessed_data) + "\n\n")

  keywords_for_pictures_filename = "preprocessed_data.pickle"
  if args.use_preprocessed_data:
    keywords_for_pictures = load_object(keywords_for_pictures_filename)
  else:
    keywords_for_pictures = synset_detection(number_of_jsons, keywords_for_pictures_filename)
  
  #tag_co_occurrence_histogram, tag_similarity_histogram, tag_list, photo_tags_dict, photo_data_list = tag_preprocessing(number_of_jsons);
  #keyword_clusters = tag_clustering(tag_list, dict(tag_co_occurrence_histogram))
  #keyword_clusters = tag_clustering(tag_list, tag_similarity_histogram)
  
  keyword_similarity_histogram = calculate_similarity_histogram(keywords_for_pictures)

  keyword_clusters = mcl_tag_clustering(keyword_similarity_histogram)

  # cluster photos
  print "Calculate photo clusters"
  photo_clusters = get_photo_clusters(keyword_clusters,keywords_for_pictures)
  print "Done"

  # write clusters to html
  clusters = defaultdict(list)
  additional_columns= {}
  additional_columns["Tags"] = []
  for index, cluster in enumerate(photo_clusters):
    additional_columns["Tags"].append(keyword_clusters[index])
    for photo_url, score in cluster:
      clusters[index].append(dict(photo_data_list[photo_url].items()+{"score":score}.items()))

  name_of_html_file = str(number_of_jsons) + "_old_q_second_smallest.html"
  write_clusters_to_html(clusters, html_file_path=name_of_html_file, additional_columns=additional_columns, open_in_browser=True)

if __name__ == '__main__':
    main()
