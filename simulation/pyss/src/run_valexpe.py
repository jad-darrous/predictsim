#!/usr/bin/python
# encoding: utf-8


import sys
import os.path
from run_simulator import parse_and_run_simulator
import multiprocessing



ouput_dir = "tmp/"
input_file = '../../../experiments/data/CEA-curie_sample/swf/log.swf'

num_processors = 80640

skip_always_done = True

pool_size = 2



execfile('../../../experiments/experiment_dicts.py')




def nice(s):
	# transform an dict into something command-line compatible, the ugliest way!
	return str(s).translate(None, " ':/(){},\"")



configs=[
	{
		'input_file': input_file,
		"num_processors":num_processors,
		'output_swf': ouput_dir+"res_"+s["name"]+"_"+nice(s["predictor"])+"_"+nice(s["corrector"])+".swf",
		'stats': False,
		"scheduler":s
	}
	for s in sched_configs]





global_expe_counter = 0

def launchExpe(options):
	global global_expe_counter
	myid = global_expe_counter
	global_expe_counter += 1
	print "Start expe "+str(myid)+" : "+str(options)
	tempout = sys.stdout
	sys.stdout = open(options["output_swf"]+".out", 'w')
	sys.stderr = sys.stdout
	if not ( skip_always_done and os.path.isfile(options["output_swf"]) ):
		parse_and_run_simulator(options)
	sys.stdout = tempout
	print "End   epxe "+str(myid)





pool = multiprocessing.Pool(processes=pool_size)
pool.map(launchExpe, configs)
pool.close() # no more tasks
pool.join()  # wrap up current tasks



























