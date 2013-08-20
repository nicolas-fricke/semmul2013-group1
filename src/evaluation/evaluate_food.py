import sys
from sets import Set
import json
import argparse
# import own modules
from clustering.pipeline import get_searchtrees_with_filenames
from helpers.general_helpers import print_status

def recursively_collect_images(siblings):
  sibling_images = Set()
  for synset in siblings:
    sibling_images |= Set([image[0].split(".")[0] for image in synset.associated_pictures])
    sibling_images |= recursively_collect_images(synset.hyponyms)
  return sibling_images

def main(args):
  print_status("Checking images against testset:\n")
  print_status("Retrieving images... \n")
  image_tree = get_searchtrees_with_filenames("food", use_meronyms=False, minimal_node_size=1)
  sys.stdout.write("Collecting images from tree... \n")
  result_ids = recursively_collect_images(image_tree)
  sys.stdout.write("Comparing images to testset... \n")

  testset_ids = json.load(open(args.testset_file, 'r')).keys()

  result_size  = len(result_ids)
  testset_size = len(testset_ids)

  true_positives = 0
  false_negatives = 0

  for testset_id in testset_ids:
    if testset_id in result_ids:
      true_positives += 1
      result_ids.remove(testset_id)
    else:
      false_negatives += 1

  false_positives = len(result_ids)

  sys.stdout.write("Done:\n\n")

  sys.stdout.write("Result size:     %d\n" % result_size)
  sys.stdout.write("Testset size:    %d\n\n" % testset_size)
  sys.stdout.write("True Positives:  %d\n" % true_positives)
  sys.stdout.write("True Negatives:  ???\n")
  sys.stdout.write("False Positives: %d\n" % false_positives)
  sys.stdout.write("False Negatives: %d\n\n" % false_negatives)
  sys.stdout.write("Precision:       %f (tp / (tp + fp))\n" % (float(true_positives) / (true_positives + false_positives)))
  sys.stdout.write("Recall:          %f (tp / (tp + fn))\n" % (float(true_positives) / (true_positives + false_negatives)))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Frontend for the Flickr image similarity evaluation programm')
  parser.add_argument('-t','--testset-file', help='Path to the testset JSON file', required=True)
  args = parser.parse_args()
  main(args)