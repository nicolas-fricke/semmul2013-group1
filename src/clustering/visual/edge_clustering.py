#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################################################
# Script crawls images from flickr and parses them in SimpleCV
#
#
# Specify the metadata folder in the config file: ../config.cfg
#
# Use config.cfg.template as template for this file
#
#
# author: nicolas fricke
# mail: nicolas.fricke@student.hpi.uni-potsdam.de
################################################################################

import ConfigParser
import json
import os.path
from collections import defaultdict
from SimpleCV import Image
from SimpleCV import EdgeHistogramFeatureExtractor
from Pycluster import kcluster
# Import own module helpers
from helpers.general_helpers import *
from helpers.visual_helpers import *

def extract_edges(image, data, slices):
  edgeExtractor = EdgeHistogramFeatureExtractor(bins=4)
  image_bins = split_image_into_slices(image, slices)
  data["edge-angles"]  = []
  data["edge-lengths"] = []
  for image_bin in image_bins:
    edge_angles_and_lengths = edgeExtractor.extract(image_bin)
    data["edge-angles"]  += edge_angles_and_lengths[:len(edge_angles_and_lengths) / 2]
    data["edge-lengths"] += edge_angles_and_lengths[len(edge_angles_and_lengths) / 2:]
  return data
