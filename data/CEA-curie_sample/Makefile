max_runtime=86400
max_procs=80640

all:filter extract predict swfs simulate

analysis:rec_abs rec mse

#logfile filtering
filter:
	../../data_manipulation/filter_swf original_swf/log_unfiltered.swf > original_swf/log.swf

#logfile feature extraction
extract:
	../../prediction/extractor.py original_swf/log.swf > original_swf/extracted_features

#logfile runtime prediction
predict:predict_sgd_squared_loss_l1 predict_tsafrir

#logfile swf generation
swfs:
	../../data_manipulation/make_all_swfs prediction_results predicted_swf original_swf/curie_sample.swf

#logfile simulation
simulate:
	../../simulation/run_simulator.sh predicted_swf $(max_procs) simulated_swf

#predictors:

#tsafrir
predict_tsafrir:
	../../prediction/predictor.py original_swf/log.swf original_swf/extracted_features prediction_results tsafrir

#sgd squared loss
predict_sgd_squared_loss_l1:
	../../prediction/predictor.py original_swf/log.swf original_swf/extracted_features prediction_results sgd squared_loss l1  onehot $(max_runtime) $(max_procs)

#extraction of specific information for data analysis:
extract_req_time:
	../../data_manipulation/extract_req_time original_swf/log.swf > prediction_results/prediction_req_time

#extraction of specific information for data analysis:
extract_run_time:
	../../data_manipulation/extract_run_time original_swf/log.swf > prediction_results/clairvoyant

analysis:mae mse rec_abs rec

analysis_monster:mae_monster mse_monster rec_abs_monster rec_monster

mse_monster:all_extract
	../../analysis/MSE_vs_t_smoothed.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions_monster) -o analysis_results/MSE.pdf -r 2

mae_monster:all_extract
	../../analysis/MAE_vs_t_smoothed.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions_monster) -o analysis_results/MAE.pdf -r 2

rec_monster:all_extract
	../../analysis/REC_-inf+inf.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions_monster) -o analysis_results/REC.pdf -r 2

rec_abs_monster:all_extract
	../../analysis/REC_abs.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions_monster) -o analysis_results/REC_ABS.pdf -r 2

mse:all_extract
	../../analysis/MSE_vs_t_smoothed.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions) -o analysis_results/MSE.pdf -r 2

mae:all_extract
	../../analysis/MAE_vs_t_smoothed.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions) -o analysis_results/MAE.pdf -r 2

rec:all_extract
	../../analysis/REC_-inf+inf.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions) -o analysis_results/REC.pdf -r 2

rec_abs:all_extract
	../../analysis/REC_abs.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions) -o analysis_results/REC_ABS.pdf -r 2

clean_swf:
	rm -f predicted_swf/* simulated_swf/*

cleanall:clean_swf
	rm -f prediction_results/* analysis_results/* original_swf/log.swf original_swf/extracted_features

