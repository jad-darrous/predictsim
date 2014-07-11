#!/bin/bash

. job_pool.sh

echoinred() {
	echo -e '\e[0;31m'"$@"
	tput sgr0
}
# afficher en bleu le premier parametre
echoinblue() {
	echo -e '\e[0;34m'"$@"
	tput sgr0
}


input_files="../data/CEA-curie_sample/predicted_swf/*.swf ../data/CEA-curie_sample/original_swf/*.swf"
# input_files="./pyss/src/sample_input ./pyss/src/5K_sample"

simulated_files_dir=../data/CEA-curie_sample/simulated_swf
# simulated_files_dir=simulated_swf

# final_csv_file=../data/CEA-curie/results.csv
final_csv_file=results.csv

algos="EasySJBFScheduler EasyBackfillScheduler"


PROCS=$(($(grep -c ^processor /proc/cpuinfo)))

# initialize the job pool to allow $PROCS parallel jobs and echo commands
job_pool_init $PROCS 1


mkdir -p $simulated_files_dir

echoinred "==== RUNNING SIMULATIONS ===="


job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd squared_epsilon_insensitive l2 onehot 86400 93312   >out_2\
job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd squared_epsilon_insensitive l1 onehot 86400 93312   >out_3\
job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd squared_epsilon_insensitive elasticnet onehot 86400 93312   >out_4\
job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd squared_loss l2 onehot 86400 93312   >out_5\
job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd squared_loss l1 onehot 86400 93312   >out_6\
job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd squared_loss elasticnet onehot 86400 93312   >out_7\
job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd huber l2 onehot 86400 93312   >out_8\
job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd huber l2 onehot 86400 93312   >out_9\
job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd huber l1 onehot 86400 93312   >out_10\
job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd epsilon_insensitive elasticnet onehot 86400 93312   >out_11\
job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd epsilon_insensitive l1 onehot 86400 93312   >out_12\
job_pool_run ./predictor.py ../../experiments/CEA-curie_cut/original_swf/curie_cut.swf ../experiments/CEA-curie_cut/original_swf/extracted_features sgd epsilon_insensitive elasticnet onehot 86400 93312   >out_13


# wait until all jobs complete before continuing
job_pool_wait
# don't forget to shut down the job pool
job_pool_shutdown

# check the $job_pool_nerrors for the number of jobs that exited non-zero
echo "job_pool_nerrors: ${job_pool_nerrors}"


echoinred "==== RUNNING ANALYSIS ===="
echoinblue Rscript simul_analysis.R $final_csv_file $simulated_files_dir/*.swf
Rscript simul_analysis.R $final_csv_file $simulated_files_dir/*.swf


echoinred "==== THE END. Results are in results.csv ===="


