mkdir -p log
(cd src && nohup python clustering/semantic/synset_detection_bestfirstsearch.py -d /20-29/20 &) > log/preprocess_synset_detection_20.log
(cd src && nohup python clustering/semantic/synset_detection_bestfirstsearch.py -d /20-29/21 &) > log/preprocess_synset_detection_21.log
(cd src && nohup python clustering/semantic/synset_detection_bestfirstsearch.py -d /20-29/22 &) > log/preprocess_synset_detection_22.log
(cd src && nohup python clustering/semantic/synset_detection_bestfirstsearch.py -d /20-29/23 &) > log/preprocess_synset_detection_23.log
(cd src && nohup python clustering/semantic/synset_detection_bestfirstsearch.py -d /20-29/24 &) > log/preprocess_synset_detection_24.log