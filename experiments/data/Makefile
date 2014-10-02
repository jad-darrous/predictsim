SWF_FOLDER:=swf
SWF_FILE:=log.swf

ANALYSIS_FOLDER:=analysis

#dry prediction stuff
MEASUREMENTS_FOLDER:=measurements
DRY_CONFIG_FOLDER:=../../dry_prediction_config
DRY_PREDICTION_FOLDER=dry_predictions
COEFFS_FOLDER=coeffs
DRY_CONFIG_FILES_FP := $(wildcard $(DRY_CONFIG_FOLDER)/*.cfg)
ALL_PREDICTION_FILES := $(patsubst $(DRY_CONFIG_FOLDER)/%.cfg,%,$(DRY_CONFIG_FILES_FP))
ALL_PREDICTION_FILES_p := $(patsubst %,%.p,$(ALL_PREDICTION_FILES))
ALL_PREDICTION_FILES_pd := $(patsubst %,%.pd,$(ALL_PREDICTION_FILES))
TERMINATED_JOBS_FP := $(patsubst %,$(DRY_PREDICTION_FOLDER)/%,$(ALL_PREDICTION_FILES))
MEASUREMENT_FILES  := $(patsubst %,$(MEASUREMENTS_FOLDER)/%,$(ALL_PREDICTION_FILES))
CUSTOM_IGNORE := $(MEASUREMENTS_FOLDER)/clairvoyant $(MEASUREMENTS_FOLDER)/tsafrir $(MEASUREMENTS_FOLDER)/reqtime
CL_FILES := $(filter-out $(CUSTOM_IGNORE),$(MEASUREMENT_FILES))
KDE_FILES := $(filter-out dry_predictions/clairvoyant,$(TERMINATED_JOBS_FP))
PRED_CPROFILE_FOLDER:=pred_cprofile

#simulation stuff
SIM_CONFIG_FOLDER :=../../simulation_config
SIM_FOLDER :=simulations
SIM_FILES_FP := $(wildcard $(SIM_CONFIG_FOLDER)/*.cfg)
ALL_SIMULATION_FILES := $(patsubst $(SIM_CONFIG_FOLDER)/%.cfg,%,$(SIM_FILES_FP))
ALL_SIMULATION_FILES_s := $(patsubst %,%.s,$(ALL_SIMULATION_FILES))
ALL_SIMULATION_FILES_sd := $(patsubst %,%.sd,$(ALL_SIMULATION_FILES))
SIM_CPROFILE_FOLDER:=sim_cprofile
ALL_SIMULATION_RESULTS := $(patsubst %,$(SIM_FOLDER)/%,$(ALL_SIMULATION_FILES))
SIM_ANALYSIS_FOLDER:=sim_analysis


all:filter
val_task1:filter predict prediction_analysis

#________________FILTERING___________________:
#filtering for simulation
filter:
	../../data_manipulation/strong_filter_all_swf swf_unfiltered swf

#TODO:_______________SIMULATION___________________:
#logfile simulation

simulate:   $(ALL_SIMULATION_FILES_s)
simulate_d:   $(ALL_SIMULATION_FILES_sd)

%.s: $(SIM_CONFIG_FOLDER)/%.cfg
	../../../simulation/pyss/src/run_simulator.py $(SWF_FOLDER)/$(SWF_FILE) $< $(SIM_FOLDER)/$(patsubst %.s,%,$@)

%.sd: $(SIM_CONFIG_FOLDER)/%.cfg
	pypy -m cProfile -o $(SIM_CPROFILE_FOLDER)/$@ ../../../simulation/pyss/src/run_simulator.py $(SWF_FOLDER)/$(SWF_FILE) $< $(SIM_FOLDER)/$(patsubst %.sd,%,$@)


#_____________DRY_PREDICTION_________________:

predict:  $(ALL_PREDICTION_FILES_p)
predict_d:  $(ALL_PREDICTION_FILES_pd)

%.p: $(DRY_CONFIG_FOLDER)/%.cfg
	../../../simulation/pyss/src/run_predictor.py $(SWF_FOLDER)/$(SWF_FILE) $< $(DRY_PREDICTION_FOLDER)/$(patsubst %.p,%,$@) $(MEASUREMENTS_FOLDER)/$(patsubst %.p,%,$@) $(COEFFS_FOLDER)/$(patsubst %.p,%,$@)

%.pd: $(DRY_CONFIG_FOLDER)/%.cfg
	pypy -m cProfile -o $(PRED_CPROFILE_FOLDER)/$@  ../../../simulation/pyss/src/run_predictor.py $(SWF_FOLDER)/$(SWF_FILE) $< $(DRY_PREDICTION_FOLDER)/$(patsubst %.pd,%,$@) $(MEASUREMENTS_FOLDER)/$(patsubst %.pd,%,$@) $(COEFFS_FOLDER)/$(patsubst %.pd,%,$@)

#_______________DRY PREDICTION ANALYSIS__________:
prediction_analysis: mae mse rec rec_abs customloss cdfs kde kde_indiv loss_average


mse:
	../../../prediction_analysis/MSE_vs_t_smoothed.R $(DRY_PREDICTION_FOLDER)/clairvoyant $(TERMINATED_JOBS_FP) -o $(ANALYSIS_FOLDER)/MSE.pdf -r 2
mae:
	../../../prediction_analysis/MAE_vs_t_smoothed.R $(DRY_PREDICTION_FOLDER)/clairvoyant $(TERMINATED_JOBS_FP)  -o $(ANALYSIS_FOLDER)/MAE.pdf -r 2
rec:
	../../../prediction_analysis/REC_-inf+inf.R $(DRY_PREDICTION_FOLDER)/clairvoyant $(TERMINATED_JOBS_FP) -o $(ANALYSIS_FOLDER)/REC.pdf -r 2
rec_abs:
	../../../prediction_analysis/REC_abs.R $(DRY_PREDICTION_FOLDER)/clairvoyant $(TERMINATED_JOBS_FP)  -o $(ANALYSIS_FOLDER)/REC_ABS.pdf -r 2
customloss:
	../../../prediction_analysis/CustomLoss_vs_t_smoothed.R $(CL_FILES) -o $(ANALYSIS_FOLDER)/custom_loss.pdf -r 2
cdfs:
	../../../prediction_analysis/compare_cdfs.R $(DRY_PREDICTION_FOLDER)/clairvoyant $(TERMINATED_JOBS_FP) -o $(ANALYSIS_FOLDER)/compare_cdfs.pdf -r 2
kde:
	../../../prediction_analysis/KDE.R $(DRY_PREDICTION_FOLDER)/clairvoyant $(KDE_FILES) -o $(ANALYSIS_FOLDER)/KDE.pdf -r 4
kde_indiv:
	../../../prediction_analysis/KDE_indiv.R $(DRY_PREDICTION_FOLDER)/clairvoyant  $(KDE_FILES) -o $(ANALYSIS_FOLDER)/KDE_indiv.pdf -r 4
loss_average:
	../../data_manipulation/average_all $(MEASUREMENTS_FOLDER)/ $(MEASUREMENTS_FOLDER)/

#___________SIMULATION_ANALYSIS__:
simulation_analysis: simu_stretch simu_metrics

simu_stretch:
	../../../simulation_analysis/swf2vis_stretchCDF_KDE.R $(ALL_SIMULATION_RESULTS)  -o $(SIM_ANALYSIS_FOLDER)/stretch.pdf -r 2

simu_metrics:
	../../../simulation_analysis/swf2vis_metrics.R $(ALL_SIMULATION_RESULTS) -o $(SIM_ANALYSIS_FOLDER)/metrics 

#_____________CLEANING___________:
clean:
	rm -rf $(DRY_PREDICTION_FOLDER)/* $(ANALYSIS_FOLDER)/* $(SWF_FOLDER)/* $(MEASUREMENTS_FOLDER)/* $(COEFFS_FOLDER)/* $(SIM_FOLDER)/* $(PRED_CPROFILE_FOLDER)/* $(SIM_CPROFILE_FOLDER)/* $(SIM_ANALYSIS_FOLDER)/*

#_____________ARCHIVED___________:
#extraction of specific information for data analysis:
#extract_req_time:
#../../data_manipulation/extract_req_time original_swf/log.swf > $(DRY_PREDICTION_FOLDER)/prediction_req_time
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
