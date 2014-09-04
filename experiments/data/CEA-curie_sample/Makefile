max_runtime=86400
max_procs=80640

all:filter

work:filter

analysis:prediction_analysis simulation_analysis

#logfile filtering
filter:
	../../data_manipulation/strong_filter_all_swf swf_unfiltered swf

#logfile runtime prediction
predict:predict_tsafrir

#logfile swf generation
swfs:
	../../data_manipulation/make_all_swfs prediction_results predicted_swf original_swf/curie_sample.swf

#filtering for simulation
filter_predictions:
	../../data_manipulation/strong_filter_all_swf predicted_swf predicted_swf_filtered

#logfile simulation
simulate:
	../../simulation/run_simulator.sh predicted_swf_filtered $(max_procs) simulated_swf

#predictors:

#tsafrir
predict_tsafrir:
	../../simulation/pyss/src/run_predictor.py  swf/log.swf ../../experiments/config/config_tsafrir dry_predictions

#sgd squared loss
#predict_sgd_squared_loss_l1:
	#../../prediction/predictor.py original_swf/log.swf original_swf/extracted_features prediction_results sgd squared_loss l1  notonehot $(max_runtime) $(max_procs)

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

clean_safe:
	rm -f predicted_swf_filtered/* predicted_swf/* prediction_results/predictions_req_time prediction_results/clairvoyant

cleanall:clean_safe
	rm -f simulated_swf/* prediction_results/* analysis_results/* original_swf/log.swf original_swf/extracted_features

