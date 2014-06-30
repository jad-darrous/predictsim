logname=curie
predictions=prediction_results/prediction_sgd prediction_results/prediction_tsafrir
predictedswf=predicted_swf/$(logname)_tsafrir.swf predicted_swf/$(logname)_sgd.swf

all: all_extract all_swf
all_extract:extract_req_time extract_run_time
all_swf:true prediction_sgd prediction_tsafrir

prediction_sgd:
	../make_swf original_swf/$(logname).swf prediction_results/prediction_sgd > predicted_swf/$(logname)_sgd.swf

prediction_tsafrir:
	../make_swf original_swf/$(logname).swf prediction_results/prediction_tsafrir > predicted_swf/$(logname)_tsafrir.swf

true:extract_run_time
	../make_swf original_swf/$(logname).swf prediction_results/true_run_time > predicted_swf/$(logname)_clairvoyant.swf

extract_req_time:
	../extract_req_time original_swf/$(logname).swf > prediction_results/prediction_req_time

extract_run_time:
	../extract_run_time original_swf/$(logname).swf > prediction_results/true_run_time

analysis:mae mse rec_abs rec

mse:all_extract
	../../analysis/MSE_vs_t_smoothed.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions) -o analysis_results/MSE.pdf -r 2

mae:all_extract
	../../analysis/MAE_vs_t_smoothed.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions) -o analysis_results/MAE.pdf -r 2

rec:all_extract
	../../analysis/REC_-inf+inf.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions) -o analysis_results/REC.pdf -r 2

rec_abs:all_extract
	../../analysis/REC_abs.R prediction_results/true_run_time prediction_results/prediction_req_time $(predictions) -o analysis_results/REC_ABS.pdf -r 2

clean:
	rm analysis_results/* prediction_results/true_run_time prediction_results/prediction_run_time $(predswf)
