mkdir -p log
(cd src && nohup python clustering/visual/combined_clustering.py -d /10 -r &) > log/preprocess_visual_data_parallel_10.log
(cd src && nohup python clustering/visual/combined_clustering.py -d /11 -r &) > log/preprocess_visual_data_parallel_11.log
(cd src && nohup python clustering/visual/combined_clustering.py -d /12 -r &) > log/preprocess_visual_data_parallel_12.log
(cd src && nohup python clustering/visual/combined_clustering.py -d /13 -r &) > log/preprocess_visual_data_parallel_13.log
(cd src && nohup python clustering/visual/combined_clustering.py -d /14 -r &) > log/preprocess_visual_data_parallel_14.log
(cd src && nohup python clustering/visual/combined_clustering.py -d /15 -r &) > log/preprocess_visual_data_parallel_15.log
(cd src && nohup python clustering/visual/combined_clustering.py -d /16 -r &) > log/preprocess_visual_data_parallel_16.log
(cd src && nohup python clustering/visual/combined_clustering.py -d /17 -r &) > log/preprocess_visual_data_parallel_17.log
(cd src && nohup python clustering/visual/combined_clustering.py -d /18 -r &) > log/preprocess_visual_data_parallel_18.log
(cd src && nohup python clustering/visual/combined_clustering.py -d /19 -r &) > log/preprocess_visual_data_parallel_19.log