#!/usr/bin/pypy
# encoding: utf-8
'''
Main script that combine everyting.

Usage:
	run.py <swf_file> [<tp>] [-r] [-o] [-s] [-w] [-f] [-a]

Options:
	-h --help			Show this help message and exit.
	-v --verbose		Be verbose.
	-o 					Online learning
'''

import sys
sys.path.append("..")

from base.docopt import docopt

from run_simulator import parse_and_run_simulator
from swf_utils import *

from io_utils import *
from batch_learning_to_rank import *
from scheduling_performance_measurement import *

from datetime import timedelta
import os
import gc

from multiprocessing import Pool

train_fn = 'train.txt'
test_fn = 'test.txt'
model_fn = 'model.txt'
score_fn = 'score.txt'


out_dir = "output"

rel = lambda fn: "%s/%s" % (out_dir, fn);

schedulers_names = [
'alpha_easy_scheduler',
'conservative_scheduler',		# Too slow
'double_conservative_scheduler',
'double_easy_backfill_scheduler',
'double_perfect_easy_backfill_scheduler',
'easy_backfill_scheduler',
'easy_plus_plus_scheduler',
'easy_prediction_backfill_scheduler',
'easy_sjbf_scheduler',
'fcfs_scheduler',
'greedy_easy_backfill_scheduler',
'head_double_easy_scheduler',
# 'lookahead_easy_backfill_scheduler',	# Tooo slow (dp)
# 'orig_probabilistic_easy_scheduler',	# Tooooooooo slow
'perfect_easy_backfill_scheduler',
'reverse_easy_scheduler',
'shrinking_easy_scheduler',
'tail_double_easy_scheduler']



def add_l2r_score(infile, scorefile, outfile):
	from itertools import izip, dropwhile
	from random import randint

	with open(infile) as fin, open(scorefile) as fscore, open(outfile, "w") as fout:
		for job_str, score_str in izip(dropwhile(swf_skip_hdr, fin), fscore):
			new_score_str = str(int(float(score_str) * 1000))
			job = [u for u in job_str.strip().split()]
			new_job_str = ' '.join(job[:-1] + [new_score_str])
			fout.write(new_job_str + '\n')


def simulate(path):
	out_swf = []
	for idx, w in enumerate(weights_options):
		config["weights"] = w
		config["input_file"] = path
		config["output_swf"] = rel("%s_%d.swf" % (simple_name(path), idx))
		parse_and_run_simulator(config)
		out_swf.append(config["output_swf"])

	return out_swf


def simulate_scheduler(path, sch_name):

	config["scheduler"]["name"] = sch_name # 'easy_sjbf_scheduler'
	config["input_file"] = path
	config["output_swf"] = rel("%s_%s.out" % (simple_name(path), sch_name))
	parse_and_run_simulator(config)
	return config["output_swf"]

def simulate_scheduler_in_memory(path, sch_name):

	config["scheduler"]["name"] = sch_name # 'easy_sjbf_scheduler'
	config["input_file"] = path
	parse_and_run_simulator(config)
	jobs = config["terminated_jobs"]
	del config["terminated_jobs"]
	return jobs


"""
This function simulates the training lists provided in the training_files
then select the best list for each backfilling priority,
and then prepare the training file of "queries" to
be fed to the learning algorithm and returns the test file name
"""
def prepare_training_set_file(training_files):

	print "[Simulating the training set..]"

	if redirect_sim_output:
		# Redirect the stdout temporary to get rid of simulator output.
		sys.stdout = open('/dev/null', 'w')

	best_all = []
	for p in training_files:
		out_swf = simulate(p)

		gc.collect() # to ensure that the output files are closed

		best = float("inf")
		for idx, swf in enumerate(out_swf):
			obj_fun_val = PerfMeasure(swf).average()
			if obj_fun_val < best:
				best = obj_fun_val
				index = idx
				outf = swf

		best_all.append(outf)
		print >> sys.__stdout__, index, best

	if redirect_sim_output:
		# Redirect the stdout again to its default state.
		sys.stdout = sys.__stdout__

	print "[Creating the ML training file..]"
	cols_matrix = [[] for i in range(len(indices))]
	for idx, fname in enumerate(best_all):
		cols = extract_columns(fname, indices)
		for i in range(len(indices)):
			cols_matrix[i].extend(cols[i])

	global min_max
	min_max = map(lambda u: (min(u), max(u)), cols_matrix)
	# print min_max

	features = []
	for idx, fname in enumerate(best_all):
		mat = extract_columns(fname, indices)
		mat = normalize_mat(mat, min_max)
		queries = convert_to_ml_format(mat, idx+1)
		features.extend(queries)

	write_lines_to_file(rel(train_fn), features)

"""
Run the training phase
"""
def training():
	print "[Training..]"
	batchL2Rlib.train(train_fn, model_fn)

"""
Give score to the jobs of the test file and compare with the
standard algorithm
"""
def sim_maui_weights(test_file):

	print "[Simulating the test file using maui..]"
	# Simulate the test file
	out_swf = simulate(test_file)
	gc.collect()

	obj_func_vals = map(lambda u: PerfMeasure(u).average(), out_swf)
	best_std_obj_func_val = min(obj_func_vals)
	best_index = obj_func_vals.index(best_std_obj_func_val)

	std_bsld = PerfMeasure(out_swf[best_index])
	std_bsld_avg, std_bsld_med, std_bsld_max = std_bsld.all()
	print "+ [MAUI] Average Bounded-Slowdown:", std_bsld_avg
	print "+ [MAUI] Median Bounded-Slowdown:", std_bsld_med
	print "+ [MAUI] Max Bounded-Slowdown:", std_bsld_max
	#print "+ [MAUI] System Utilization:", compute_utilisation(out_swf[best_index])

	res_data.extend([str(u) for u in (std_bsld_avg, std_bsld_med, std_bsld_max)])

	return (std_bsld_avg, std_bsld_med, std_bsld_max)


def classify_and_eval_h(test_file):

	global min_max

	print "[Creating the ML testing file..]"
	mat = extract_columns(test_file, indices)
	mat = normalize_mat(mat, min_max)
	features = convert_to_ml_format(mat, 0)

	write_lines_to_file(rel(test_fn), features)

	print "[Classifying/Testing..]"
	batchL2Rlib.classify(test_fn, model_fn, score_fn)


	print "[Simulating the test file using L2R..]"
	# add the l2r to the test log as the think time.
	test_l2r_fn = "%s_with_score.swf" % test_file.split('.')[0]
	add_l2r_score(test_file, rel(score_fn), test_l2r_fn)

	# Simulate the file after l2r
	config["scheduler"]["name"] = 'l2r_maui_scheduler'
	config["weights"] = (0, 0, 0, 0, 0, 0, 1)
	config["input_file"] = test_l2r_fn
	config["output_swf"] = "%s_sim.swf" % test_l2r_fn.split('.')[0]
	parse_and_run_simulator(config)

	l2r_bsld = PerfMeasure(config["output_swf"])
	l2r_bsld_avg, l2r_bsld_med, l2r_bsld_max = l2r_bsld.all()
	print "+ [L2R] Average Bounded-Slowdown:", l2r_bsld_avg
	print "+ [L2R] Median Bounded-Slowdown:", l2r_bsld_med
	print "+ [L2R] Max Bounded-Slowdown:", l2r_bsld_max
	#print "+ [L2R] System Utilization:", compute_utilisation(config["output_swf"])

	res_data.extend([str(u) for u in (l2r_bsld_avg, l2r_bsld_med, l2r_bsld_max)])
	res_data.append(' ')

	return (l2r_bsld_avg, l2r_bsld_med, l2r_bsld_max)


def classify_and_eval_h_rand(test_file):

	def add_l2r_score_rand(infile, outfile):
		from itertools import izip, dropwhile
		from random import randint, seed
		seed()
		with open(infile) as fin, open(outfile, "w") as fout:
			for job_str in dropwhile(swf_skip_hdr, fin):
				new_score_str = str(randint(0, 1000000))
				job = [u for u in job_str.strip().split()]
				new_job_str = ' '.join(job[:-1] + [new_score_str])
				fout.write(new_job_str + '\n')


	print "[Simulating the test file using L2R..]"
	test_l2r_fn = "%s_with_score.swf" % test_file.split('.')[0]
	add_l2r_score_rand(test_file, test_l2r_fn)

	# Simulate the file after l2r
	config["scheduler"]["name"] = 'l2r_maui_scheduler'
	config["weights"] = (0, 0, 0, 0, 0, 0, 1)
	config["input_file"] = test_l2r_fn
	config["output_swf"] = "%s_rnd_sim.swf" % test_l2r_fn.split('.')[0]
	parse_and_run_simulator(config)

	l2r_bsld = PerfMeasure(config["output_swf"])
	l2r_bsld_avg, l2r_bsld_med, l2r_bsld_max = l2r_bsld.all()
	print "+ [RND] Average Bounded-Slowdown:", l2r_bsld_avg
	print "+ [RND] Median Bounded-Slowdown:", l2r_bsld_med
	print "+ [RND] Max Bounded-Slowdown:", l2r_bsld_max

	return (l2r_bsld_avg, l2r_bsld_med, l2r_bsld_max)


def sim_statistics(test_file, sch_name):

	print "[Simulation using", sch_name, "]"
	sim_out = simulate_scheduler(test_file, sch_name)
	l2r_bsld = PerfMeasure(sim_out)
	l2r_bsld_avg, l2r_bsld_med, l2r_bsld_max = l2r_bsld.all()
	print "+ Average Bounded-Slowdown:", l2r_bsld_avg
	print "+ Median Bounded-Slowdown:", l2r_bsld_med
	print "+ Max Bounded-Slowdown:", l2r_bsld_max
	return (l2r_bsld_avg, l2r_bsld_med, l2r_bsld_max)

def sim_statistics_x(test_file, sch_name):

	print "\n[Simulation using", sch_name, "]"
	sim_jobs = simulate_scheduler_in_memory(test_file, sch_name)
	l2r_bsld = PerfMeasure(jobs=sim_jobs)
	l2r_bsld_avg, l2r_bsld_med, l2r_bsld_max = l2r_bsld.all()
	print "+ Average Bounded-Slowdown:", l2r_bsld_avg
	print "+ Median Bounded-Slowdown:", l2r_bsld_med
	print "+ Max Bounded-Slowdown:", l2r_bsld_max
	return (l2r_bsld_avg, l2r_bsld_med, l2r_bsld_max)


def sim_all_schedulers(swf_path, dt=None):

	if dt is None: dt = {}

	# schedulers_names=['greedy_easy_backfill_scheduler','easy_sjbf_scheduler','fcfs_scheduler',]
	for scheduler_name in schedulers_names:
		try:
			dt[scheduler_name] = sim_statistics(swf_path, scheduler_name)
		except:
			dt[scheduler_name] = (float("Inf"),float("Inf"),float("Inf"))
		print

	# p = Pool(5)
	# vals = p.map(f, schedulers_names)

	ls = map(lambda u: (u, dt[u][0]), dt)
	ls.sort(key=lambda u: u[1])
	print
	for p in ls:
		print p[0], dt[p[0]]



PerfMeasure = Slowdown
PerfMeasure = BoundedSlowdown
batchL2Rlib = RankLib(out_dir)
batchL2Rlib = SophiaML(out_dir)
batchL2Rlib = SVM_Rank(out_dir)

redirect_sim_output = True

random_weights = True


res_data = []
def append_results():
	with open("results/results.txt", "a") as myfile:
		myfile.write('\t'.join(res_data) + '\n')


if __name__ == "__main__":

	arguments = docopt(__doc__, version='1.0.0rc2')

	os.system("date")

	config = {
		"scheduler": {
			"name":'maui_scheduler',
			"progressbar": False,
			# "predictor":{"name":'predictor_clairvoyant'},
			# "predictor":{"name":'predictor_tsafrir'},
			# "predictor":{"name":'predictor_reqtime'},
			# "predictor":{"name":'predictor_double_reqtime'},
			# "predictor":{"name":'predictor_my'},
			# "predictor":{"name":'predictor_sgdlinear', 'gd': 'NAG', 'loss': 'composite', 'rightside': 'square', 'weight': '1+log(m*r)', 'cubic': False, 'regularization': 'l2', 'max_cores': 'auto', 'eta': 5000, 'leftparam': 1, 'leftside': 'abs', 'threshold': 0, 'quadratic': True, 'rightparam': 1, 'lambda': 4000000000},
			# "predictor":{"name":'predictor_sgdlinear', "quadratic":True, "cubic": False, "loss":"squaredloss", "gd":"NAG", "eta": 0.1, "weight": False},
			# "corrector":{"name":'recursive_doubling'}
			# "corrector":{"name":'tsafrir'}
			},
		"num_processors": 80640, # depend on the swf log
		"stats": False,
		"verbose": False
	}

	log_path = arguments["<swf_file>"]
	fname = simple_name(log_path)

	res_data.append(fname + '\t')

	execfile("conf.py")

	config["num_processors"] = getMaxProcs(log_path)

	if "CEA" in arguments["<swf_file>"]: config["num_processors"] = 80640

	redirect_sim_output = arguments["-r"]

	print config

	# simulate with all the schedulers
	if arguments["-s"]:
		sim_all_schedulers(log_path)

	# do online learning
	if arguments["-o"]:
		config["weights"] = (0, 0, 0, 0, 0, 0, +1)
		sim_statistics(log_path, 'online_l2r_maui_scheduler')

	# simulate with all the schedulers
	if arguments["-a"]:
		sim_statistics(log_path, 'adaptive_maui_scheduler')

	# simulate with diff weights
	if arguments["-w"]:
		if redirect_sim_output:	sys.stdout = open('/dev/null', 'w')

		vals = []
		try:
			for w in weights_options:
				config["weights"] = w
				config["input_file"] = log_path
				parse_and_run_simulator(config)
				sim_jobs = config["terminated_jobs"]
				del config["terminated_jobs"]
				obj_fun_val = PerfMeasure(jobs=sim_jobs).average()
				vals.append((w, obj_fun_val))
				print >> sys.__stdout__, vals[-1]
		except:
			pass
		vals.sort(key= lambda u: u[1])
		print >> sys.__stdout__
		for i in range(min(10, len(vals))):
			print >> sys.__stdout__, vals[i]

		if redirect_sim_output: sys.stdout = sys.__stdout__

	# train offline
	if arguments["-f"]:
		if arguments["<tp>"] is not None:
			training_parts = int(arguments["<tp>"])

		res_data.extend([str(training_parts), ' '])

		os.system("rm -f %s/*" % out_dir)

		training_files, test_file = split_swf(\
			log_path, training_percentage, training_parts, dir=out_dir)

		if 1:
			prepare_training_set_file(training_files)
			training()

		dt = {}

		print "--{ Evaluate on the test set }--"
		dt["maui"] = sim_maui_weights(test_file)
		dt["L2R"] = classify_and_eval_h(test_file)
		dt["l2r_rand"] = classify_and_eval_h_rand(test_file)

		# sim_all_schedulers(test_file, dt)

		append_results()

