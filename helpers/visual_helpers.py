from SimpleCV import Image
from math import sqrt

def split_image_into_bins(image, bins):
  bins_sqrt = int(sqrt(bins))
  if bins != bins_sqrt ** 2:
    raise Exception("Number of bins must be a square root")
  step_width  = image.width  / bins_sqrt
  step_height = image.height / bins_sqrt
  image_slices = []
  # Last few pixels get lost, if width mod bins_sqrt != 0
  for pos_height in range(0, step_height * bins_sqrt, step_height):
    for pos_width in range(0, step_width * bins_sqrt, step_width):
      image_slices.append(image.crop(pos_width, pos_height, step_width, step_height))
  return tuple(image_slices)