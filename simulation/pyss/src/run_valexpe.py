#!/usr/bin/python
# encoding: utf-8


import sys
import os.path
from run_simulator import parse_and_run_simulator
import multiprocessing
import pprint

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



ouput_dir = "tmp/"
input_file = '../../../experiments/data/CEA-curie_sample/swf/log.swf'

num_processors = 80640

skip_always_done = True

pool_size = 8



execfile('../../../experiments/experiment_dicts.py')




def nice(s):
	# transform an dict into something command-line compatible, the ugliest way!
	return str(s).translate(None, " ':/(){},\"").replace("name", "").replace("predictor_sgdlinear", "gdl").replace("max_coresauto", "").replace("regularizationl2", "").replace("lambda4000000000", "").replace("gdNAG", "")



configs=[
	{
		'input_file': input_file,
		"num_processors":num_processors,
		'output_swf': ouput_dir+"res_"+s["name"]+"_"+nice(s["predictor"])+"_"+nice(s["corrector"])+".swf",
		'stats': False,
		"scheduler":s
	}
	for s in sched_configs]


import threading
iid = 1
iid_lock = threading.Lock()

def next_id():
    global iid
    with iid_lock:
        result = iid
        iid += 1
    return result




def launchExpe(options):
	myid = next_id()
	
	if not ( skip_always_done and os.path.isfile(options["output_swf"]) ):
		print bcolors.WARNING+"Start expe "+str(myid)+ bcolors.ENDC+" : "+str(options)
		error = False
		tempout = sys.stdout
		sys.stdout = open(options["output_swf"]+".out", 'w')
		sys.stderr = sys.stdout
		try:
			parse_and_run_simulator(options)
		except Exception,e:
			print "Exception: "+str(e)
			error = str(e)
		sys.stdout = tempout
		if not error:
			print bcolors.OKBLUE+"End   epxe "+str(myid)+ bcolors.ENDC
		else:
			print bcolors.FAIL+"ERROR on "+str(myid)+": "+str(e)+ bcolors.ENDC
	else:
		print bcolors.OKGREEN+"Already done"+str(myid)+ bcolors.ENDC+" : "+str(options)




pool = multiprocessing.Pool(processes=pool_size)
pool.map(launchExpe, configs)
pool.close() # no more tasks
pool.join()  # wrap up current tasks
























