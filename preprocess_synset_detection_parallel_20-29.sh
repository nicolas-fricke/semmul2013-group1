mkdir -p log
(cd src && nohup python clustering/semantic/synset_detection_bestfirstsearch.py -d /20-29/20 &) > log/preprocess_synset_detection_20.log
(cd src && nohup python clustering/semantic/synset_detection_bestfirstsearch.py -d /20-29/21 &) > log/preprocess_synset_detection_21.log
