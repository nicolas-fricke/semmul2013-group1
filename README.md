# Semantic Multimedia 2013 – Group 1

[HPI Seminar on Semantic Multimedia](http://semmul2013.blogspot.de/), summer semester 2013

We are group 1 – [Mandy Roick](https://github.com/Mandy-Roick), [Claudia Exeler](https://github.com/claudia-exeler), [Tino Junge](https://github.com/tino-junge), and [Nicolas Fricke](https://github.com/nicolas-fricke)

Our objective is to analyze Images on Flickr and build homogenous clusters of the results.
Read more: http://semmul2013.blogspot.de/2013/04/seminar-challenge.html [german]


## Installation instructions on Debian 7

### clone git repository
``` bash
$ sudo apt-get install git # only if you do not have git already
$ git clone https://github.com/nicolas-fricke/semmul2013-group1.git
```

### install python packages
``` bash
$ sudo apt-get install python-pip
$ sudo pip install flask
$ sudo pip install flask_assets
$ sudo pip install nltk
$ sudo pip install SimpleCV
$ sudo pip install Pycluster

$ sudo apt-get install python-scipy python-pygame python-opencv mcl
```

### download wordnet for python
open a python console
``` bash
$ python
```
and use nltk to download an offline instance of wordnet
``` python 
>>> import nltk
>>> nltk.download()
	# opens download tool
	# enter d for download
	# enter wordnet for downloading wordnet
	# enter q for quit
```

### configuration
``` bash
$ cd semmul2013-group1/
$ cp config.cfg.template config.cfg
$ vim config.cfg
# adapt config: 
# 	1. data-dir: should be the path to the folder, where metadata and images can be found, for example .../semmul2013-group1/data/
#	2. metadata-dir: should be the path to the folder, where metadata jsons for Flickr-images can be found, for example .../semmul2013-group1/data/metadata
#		-> folder structure should be: metadata/10-19/10/100210.json
#	3. downloaded-images-dir: if Flickr-images are already downloaded, this is the path to the folder, where they can be found
#	4. preprocessed-data-dir: should be the path to the folder, where preprocessed data can be stored, for example .../semmul2013-group1/data/preprocessed_data
```

### preprocessing and starting of program
``` bash
$ cd src/
$ export PYTHONPATH=$PYTHONPATH:`pwd`

$ python clustering/semantic/preprocess_synset_detection_bestfirstsearch.py # can be processed in parallel by using parameter -d
$ python clustering/semantic/preprocess_keyword_clusters.py
$ python clustering/visual/preprocess_visual_features.py # can be processed in parallel by using parameter -d
$ python frontend/frontend.py
```
