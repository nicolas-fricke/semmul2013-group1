import ConfigParser
import sys
import urllib2

def parse_datafile(file_name):
  data = {}
  for line in open(file_name):
    line = line.strip()
    key, value = tuple(entry.strip() for entry in line.split(':', 1))
    data[key] = value
  return data

def url_exists(url):
  try:
    r = urllib2.urlopen(url)
  except urllib2.URLError as e:
    r = e
    return False
  return r.code == 200

def main():
  # import configuration
  config = ConfigParser.SafeConfigParser()
  config.read('../config.cfg')

  api_key = config.get('Flickr API Key', 'key')
  metadata_dir = '../' + config.get('Directories', 'metadata-dir')

  # open metadata file
  data = parse_datafile(metadata_dir + '/10-19/10/100000.txt')
  print url_exists(data.get('Web url'))

if __name__ == '__main__':
    main()
