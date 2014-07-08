logname=curie_cut
header="; MaxProcs: 11520"

all: make_swfs

make_swfs:extract_run_time extract_req_time
	../../data_manipulation/make_all_swfs prediction_results predicted_swf original_swf/$(logname).swf $(header)

extract_req_time:
	../../data_manipulation/extract_req_time original_swf/$(logname).swf > prediction_results/prediction_req_time

extract_run_time:
	../../data_manipulation/extract_run_time original_swf/$(logname).swf > prediction_results/clairvoyant

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

clean:
	rm predicted_swf/* prediction_results/prediction_req_time prediction_results/clairvoyant
