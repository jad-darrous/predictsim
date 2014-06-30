logname=curie

all:extract_req_time extract_run_time sgd tsafrir true

sgd:
	../make_swf original_swf/$(logname).swf prediction_results/prediction_sgd > predicted_swf/$(logname)_sgd.swf

tsafrir:
	../make_swf original_swf/$(logname).swf prediction_results/prediction_tsafrir > predicted_swf/$(logname)_tsafrir.swf

true:
	../make_swf original_swf/$(logname).swf prediction_results/true_run_time > predicted_swf/$(logname)_clairvoyant.swf

extract_req_time:
	../extract_req_time original_swf/$(logname).swf > prediction_results/prediction_req_time

extract_run_time:
	../extract_run_time original_swf/$(logname).swf > prediction_results/true_run_time
