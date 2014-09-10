MEASUREMENTS_FOLDER:=measurements
CONFIG_FOLDER:=../../config

CONFIG_FILES_FP := $(wildcard ../../config/*.cfg)
ALL_PREDICTION_FILES := $(patsubst ../../config/%.cfg,%,$(CONFIG_FILES_FP))
TERMINATED_JOBS_FP := $(patsubst %,dry_predictions/%,$(ALL_PREDICTION_FILES))
MEASUREMENT_FILES  := $(patsubst %,$(MEASUREMENTS_FOLDER)/%,$(ALL_PREDICTION_FILES))
CUSTOM_IGNORE := $(MEASUREMENTS_FOLDER)/clairvoyant $(MEASUREMENTS_FOLDER)/tsafrir $(MEASUREMENTS_FOLDER)/reqtime
CL_FILES := $(filter-out $(CUSTOM_IGNORE),$(MEASUREMENT_FILES))
KDE_FILES := $(filter-out dry_predictions/clairvoyant,$(TERMINATED_JOBS_FP))

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

predict: $(ALL_PREDICTION_FILES)

%: ../../config/%.cfg
	../../../simulation/pyss/src/run_predictor.py swf/log.swf $< dry_predictions/$@ $(MEASUREMENTS_FOLDER)/$@ coeffs/$@

#_______________DRY PREDICTION ANALYSIS__________:
prediction_analysis: mae mse rec rec_abs customloss cdfs kde kde_indiv loss_average


mse:
	../../../prediction_analysis/MSE_vs_t_smoothed.R dry_predictions/clairvoyant $(TERMINATED_JOBS_FP) -o analysis/MSE.pdf -r 2
mae:
	../../../prediction_analysis/MAE_vs_t_smoothed.R dry_predictions/clairvoyant $(TERMINATED_JOBS_FP)  -o analysis/MAE.pdf -r 2
rec:
	../../../prediction_analysis/REC_-inf+inf.R dry_predictions/clairvoyant $(TERMINATED_JOBS_FP) -o analysis/REC.pdf -r 2
rec_abs:
	../../../prediction_analysis/REC_abs.R dry_predictions/clairvoyant $(TERMINATED_JOBS_FP)  -o analysis/REC_ABS.pdf -r 2
customloss:
	../../../prediction_analysis/CustomLoss_vs_t_smoothed.R $(CL_FILES) -o analysis/custom_loss.pdf -r 2
cdfs:
	../../../prediction_analysis/compare_cdfs.R dry_predictions/clairvoyant $(TERMINATED_JOBS_FP) -o analysis/compare_cdfs.pdf -r 2
kde:
	../../../prediction_analysis/KDE.R  $(KDE_FILES) -o analysis/KDE.pdf -r 4
kde_indiv:
	../../../prediction_analysis/KDE_indiv.R dry_predictions/clairvoyant  $(KDE_FILES) -o analysis/KDE_indiv.pdf -r 4
loss_average:
	../../data_manipulation/average_all $(MEASUREMENTS_FOLDER)/ $(MEASUREMENTS_FOLDER)/

#_____________CLEANING___________:
clean:
	rm -rf dry_predictions/* analysis/* swf/* $(MEASUREMENTS_FOLDER)/* coeffs/*

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
