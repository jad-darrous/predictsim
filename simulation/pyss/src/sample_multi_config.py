#! /usr/bin/env python2

from run_simulator import parse_and_run_simulator

options = {
"scheduler" : {
	"name":'TBD'
	},
"input_file": '../../../data/CEA-curie_sample/original_swf/log.swf',
"num_processors" : 80640,
"stats" : False,
"output_swf" : 'TBD'
}

for sched in ('easy_backfill_scheduler', "easy_sjbf_scheduler"):
	options["scheduler"]["name"] = sched
	options["output_swf"] = "res_"+sched+".swf"
	parse_and_run_simulator(options)
