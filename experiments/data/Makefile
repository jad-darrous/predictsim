max_runtime=86400
max_procs=80640

all:filter

#________________FILTERING___________________:
#filtering for simulation
filter:
	../../data_manipulation/weak_filter_swf original_swf/log_unfiltered.swf > original_swf/log.swf

#_______________SIMULATION___________________:
#logfile simulation
simulate:
	../../simulation/run_simulator.sh predicted_swf_filtered $(max_procs) simulated_swf

#_____________DRY_PREDICTION_________________:

#tsafrir
predict_tsafrir:
	../../simulation/run_predictor.sh predicted_swf_filtered $(max_procs) simulated_swf

#tsafrir
predict_tsafrir:
	../../prediction/predictor.py original_swf/log.swf original_swf/extracted_features prediction_results tsafrir

#sgd squared loss
predict_sgd_squared_loss_l1:
	../../prediction/predictor.py original_swf/log.swf original_swf/extracted_features prediction_results sgd squared_loss l1  notonehot $(max_runtime) $(max_procs)

#extraction of specific information for data analysis:
extract_req_time:
	../../data_manipulation/extract_req_time original_swf/log.swf > prediction_results/prediction_req_time

#extraction of specific information for data analysis:
extract_run_time:
	../../data_manipulation/extract_run_time original_swf/log.swf > prediction_results/clairvoyant

simulation_analysis:
	../../simulation_analysis/swf2vis_metrics.R simulated_swf/* -o /tmp/truc > analysis_results/metrics

prediction_analysis:mae mse rec_abs rec

mse:extract_run_time extract_req_time
	../../prediction_analysis/MSE_vs_t_smoothed.R prediction_results/* -o analysis_results/MSE.pdf -r 2

mae:extract_run_time extract_req_time
	../../prediction_analysis/MAE_vs_t_smoothed.R prediction_results/*  -o analysis_results/MAE.pdf -r 2

rec:extract_run_time extract_req_time
	../../prediction_analysis/REC_-inf+inf.R prediction_results/* -o analysis_results/REC.pdf -r 2

rec_abs:extract_run_time extract_req_time
	../../prediction_analysis/REC_abs.R prediction_results/*  -o analysis_results/REC_ABS.pdf -r 2

#_____________ARCHIVED___________:

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
