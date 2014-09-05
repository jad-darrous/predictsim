max_runtime=86400
max_procs=80640

all:filter
val_task1:filter predict prediction_analysis

#________________FILTERING___________________:
#filtering for simulation
filter:
	../../data_manipulation/strong_filter_all_swf swf_unfiltered swf

#TODO:_______________SIMULATION___________________:
#logfile simulation
simulate:
	../../simulation/run_simulator.sh predicted_swf_filtered $(max_procs) simulated_swf

#_____________DRY_PREDICTION_________________:
CONFIG_FILES := $(wildcard ../../config/*.cfg)
ALL_PREDICTION_FILES = $(patsubst ../../config/%.cfg,%,$(CONFIG_FILES))
TERMINATED_JOBS_FP := $(wildcard dry_predictions/*)
TERMINATED_JOBS=  $(patsubst dry_predictions/%,%,$(TERMINATED_JOBS_FP))
PREDICTION_FILES = $(filter-out $(TERMINATED_JOBS),$(ALL_PREDICTION_FILES))

predict: $(PREDICTION_FILES)

%: ../../config/%.cfg
	../../../simulation/pyss/src/run_predictor.py swf/log.swf $< dry_predictions/$@

#_______________DRY PREDICTION ANALYSIS__________:
prediction_analysis: mae mse rec_abs rec cdfs

mse:
	../../../prediction_analysis/MSE_vs_t_smoothed.R dry_predictions/clairvoyant dry_predictions/* -o analysis/MSE.pdf -r 2
mae:
	../../../prediction_analysis/MAE_vs_t_smoothed.R dry_predictions/clairvoyant dry_predictions/*  -o analysis/MAE.pdf -r 2
rec:
	../../../prediction_analysis/REC_-inf+inf.R dry_predictions/clairvoyant dry_predictions/* -o analysis/REC.pdf -r 2
rec_abs:
	../../../prediction_analysis/REC_abs.R dry_predictions/clairvoyant dry_predictions/*  -o analysis/REC_ABS.pdf -r 2
cdfs:
	../../../prediction_analysis/compare_cdfs.R dry_predictions/clairvoyant dry_predictions/*  -o analysis/compare_cdfs.pdf -r 2



#_____________ARCHIVED___________:
#extraction of specific information for data analysis:
#extract_req_time:
#../../data_manipulation/extract_req_time original_swf/log.swf > dry_predictions/prediction_req_time
#extraction of specific information for data analysis:
#extract_run_time:
#../../data_manipulation/extract_run_time original_swf/log.swf > prediction_results/clairvoyant
#simulation_analysis:
#../../simulation_analysis/swf2vis_metrics.R simulated_swf/* -o /tmp/truc > analysis_results/metrics
#prediction_analysis:mae mse rec_abs rec
#mse:extract_run_time extract_req_time
#../../prediction_analysis/MSE_vs_t_smoothed.R prediction_results/* -o analysis_results/MSE.pdf -r 2
#mae:extract_run_time extract_req_time
#../../prediction_analysis/MAE_vs_t_smoothed.R prediction_results/*  -o analysis_results/MAE.pdf -r 2
#rec:extract_run_time extract_req_time
#../../prediction_analysis/REC_-inf+inf.R prediction_results/* -o analysis_results/REC.pdf -r 2
#rec_abs:extract_run_time extract_req_time
#../../prediction_analysis/REC_abs.R prediction_results/*  -o analysis_results/REC_ABS.pdf -r 2
#clean_safe:
#rm -f predicted_swf_filtered/* predicted_swf/* prediction_results/predictions_req_time prediction_results/clairvoyant
#cleanall:clean_safe
#rm -f simulated_swf/* prediction_results/* analysis_results/* original_swf/log.swf original_swf/extracted_features
#archived:
#logfile swf generation
#swfs:
#../../data_manipulation/make_all_swfs prediction_results predicted_swf original_swf/curie_sample.swf
#logfile feature extraction
#extract:
#../../prediction/extractor.py original_swf/log.swf > original_swf/extracted_features
#work:filter extract predict swfs filter_predictions simulate
#analysis:prediction_analysis simulation_analysis
