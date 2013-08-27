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

import argparse
import ConfigParser
import json
import numpy as np
import os.path
from collections import defaultdict
from SimpleCV import Image
from math import sqrt
from scipy.cluster.hierarchy import fclusterdata as hierarchial_cluster
from Pycluster import kcluster
# Import own module helpers
import sys
from helpers.general_helpers import *
from helpers.visual_helpers import *

def extract_colors(image, data, slices):
  (value, saturation, hue) = image.splitChannels()
  bins = zip(split_image_into_slices(hue, slices), split_image_into_slices(saturation.equalize(), slices), split_image_into_slices(value.equalize(), slices))
  data["colors"] = []
  for hue_bin, sat_bin, val_bin in bins:
    data["colors"] += hue_bin.histogram(20)
    data["colors"] += sat_bin.histogram(20)
    data["colors"] += val_bin.histogram(20)
  return data
