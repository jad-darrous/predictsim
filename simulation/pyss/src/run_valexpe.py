#! /usr/bin/env python2
import os.path

from run_simulator import parse_and_run_simulator



ouput_dir = "tmp/"
input_file = '../../../data/CEA-curie_sample/original_swf/log.swf'

skip_always_done = True


options = {
"scheduler" : {
	"name":'TBD',
	'predictor': {"name":"TBD"},
	'corrector': {"name":"TBD"},
	},
"input_file": input_file,
"num_processors" : 80640,
"stats" : False,
"output_swf" : 'TBD'
}


scheds_without_predictors = ('easy_backfill_scheduler', "easy_sjbf_scheduler")
scheds_with_predictors = ('easy_plus_plus_scheduler', 'easy_prediction_backfill_scheduler')

predictors_without_correctors = ("predictor_clairvoyant", "predictor_reqtime", "predictor_double_reqtime")
predictors_with_correctors = ("predictor_sgdlinear", "predictor_sgdlinear_simple", "predictor_tsafrir")

correctors = ("reqtime", "tsafrir", "recursive_doubling")

for sched in scheds_without_predictors:
	options["scheduler"]["name"] = sched
	options["output_swf"] = ouput_dir+"res_"+sched+".swf"
	if not ( skip_always_done and os.path.isfile(options["output_swf"]) ):
		parse_and_run_simulator(options)

for sched in scheds_with_predictors:
	options["scheduler"]["name"] = sched
	
	#we set a corrector, but it will not be used
	options["scheduler"]["corrector"]["name"] = "reqtime"
	for pred in predictors_without_correctors:
		options["scheduler"]["predictor"]["name"] = pred
		options["output_swf"] = ouput_dir+"res_"+sched+"_"+pred+".swf"
		if not ( skip_always_done and os.path.isfile(options["output_swf"]) ):
			parse_and_run_simulator(options)
	
	
	for pred in predictors_with_correctors:
		options["scheduler"]["predictor"]["name"] = pred
		for corr in correctors:
			options["scheduler"]["corrector"]["name"] = corr
			options["output_swf"] = ouput_dir+"res_"+sched+"_"+pred+"_"+corr+".swf"
			if not ( skip_always_done and os.path.isfile(options["output_swf"]) ):
				parse_and_run_simulator(options)
