#!/usr/bin/pypy
# encoding: utf-8
'''
Main script that combine everyting.

Usage:
	run.py <swf_file> [<tp>]

Options:
	-h --help			Show this help message and exit.
	-v --verbose		Be verbose.
'''

import sys
sys.path.append("..")

from base.docopt import docopt

from run_simulator import parse_and_run_simulator
from swf_utils import *

from batch_learning_to_rank import *
from scheduling_performance_measurement import *

from datetime import timedelta
import os
import gc


train_fn = 'train.txt'
test_fn = 'test.txt'
model_fn = 'model.txt'
score_fn = 'score.txt'


out_dir = "output"

rel = lambda fn: "%s/%s" % (out_dir, fn);


def write_str_to_file(fname, _str):
	with open(fname, 'w') as f:
		f.write(_str)
		# assert f.write(_str) == len(_str)

def write_lines_to_file(fname, lines):
	# write_str_to_file(fname, '\n'.join(lines))
	# return
	with open(fname, 'w') as f:
		f.writelines("%s\n" % line for line in lines)


def add_l2r_score(infile, scorefile, outfile):
	from itertools import izip, dropwhile

	with open(infile) as fin, open(scorefile) as fscore, open(outfile, "w") as fout:
		for job_str, score_str in izip(dropwhile(swf_skip_hdr, fin), fscore):
			new_score_str = str(int(float(score_str) * 1000))
			job = [u for u in job_str.strip().split()]
			new_job_str = ' '.join(job[:-1] + [new_score_str])
			fout.write(new_job_str + '\n')

def simulate(fname):
	out_swf = []
	for idx, w in enumerate(weights_options):
		config["weights"] = w
		config["input_file"] = fname
		config["output_swf"] = "%s_%d.swf" % (fname.split('.')[0], idx)
		parse_and_run_simulator(config)
		out_swf.append(config["output_swf"])
	return out_swf


"""
This function takes the original log file, split it and simulate
the training lists then select the best list for each backfilling
priority, and then prepare the training file of "queries" to
be fed to the learning algorithm and returns the test file name
"""
def split_and_simulate(fname):

	os.system("rm -f %s/*" % out_dir)

	out_files, test_file = split_swf(fname, training_percentage, training_parts, dir=out_dir)

	print "[Simulating the training set..]"

	best_all = []
	for p in out_files:
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
		print index, best

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

	return test_file

"""
Run the training phase
"""
def training():
	print "[Training..]"
	batchL2Rlib.train(train_fn, model_fn)

"""
Give score to the jobs of the test file and compare wit the
standard algorithm
"""
def classify_and_eval_h(test_file):

	global min_max

	print "[Creating the ML testing file..]"
	mat = extract_columns(test_file, indices)
	mat = normalize_mat(mat, min_max)
	features = convert_to_ml_format(mat, 0)

	write_lines_to_file(rel(test_fn), features)

	print "[Simulating the test file..]"
	# Simulate the test file
	out_swf = simulate(test_file)
	gc.collect()

	obj_func_vals = map(lambda u: PerfMeasure(u).average(), out_swf)
	best_std_obj_func_val = min(obj_func_vals)
	best_index = obj_func_vals.index(best_std_obj_func_val)

	std_bsld = PerfMeasure(out_swf[best_index])
	std_bsld_avg, std_bsld_med, std_bsld_max = std_bsld.all()
	print "+ [STD] Average Bounded-Slowdown:", std_bsld_avg
	print "+ [STD] Median Bounded-Slowdown:", std_bsld_med
	print "+ [STD] Max Bounded-Slowdown:", std_bsld_max
	print "+ [STD] System Utilization:", compute_utilisation(out_swf[best_index])


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
	print "+ [L2R] System Utilization:", compute_utilisation(config["output_swf"])

	res_data.extend([str(u) for u in (std_bsld_avg, std_bsld_med, std_bsld_max)])
	res_data.extend([str(u) for u in (l2r_bsld_avg, l2r_bsld_med, l2r_bsld_max)])
	res_data.append(' ')



PerfMeasure = Slowdown
PerfMeasure = BoundedSlowdown
batchL2Rlib = RankLib(out_dir)
batchL2Rlib = SophiaML(out_dir)
batchL2Rlib = SVM_Rank(out_dir)



res_data = []
def append_results():
	with open("results/results.txt", "a") as myfile:
		myfile.write('\t'.join(res_data) + '\n')


if __name__ == "__main__":

	arguments = docopt(__doc__, version='1.0.0rc2')

	os.system("date")

	config = {
		"scheduler": {"name":'maui_scheduler', "progressbar": False},
		"num_processors": 80640, # depend on the swf log
		"stats": False,
		"verbose": False
	}

	log_path = arguments["<swf_file>"]
	fname = os.path.basename(log_path)

	res_data.append(fname + '\t')

	execfile("conf.py")
	
	config["num_processors"] = getMaxProcs(log_path)

	if "CEA" in arguments["<swf_file>"]: config["num_processors"] = 80640

	if "<tp>" in arguments:
		training_parts = int(arguments["<tp>"])

	res_data.extend([str(training_parts), ' '])

	try:
		import shutil
		shutil.copy(log_path, ".")

		if 1:
			test_file = split_and_simulate(fname)
		else:
			test_file = "%s/%s_test.swf" % (out_dir, fname.split('.')[0])
			if 0: os.system("cp " + fname + " " + test_file)

		if 1: training()

		print "--- Test on the test set"
		classify_and_eval_h(test_file)

		# print "--- Test on the training set"
		# os.system("cp " + fname + " " + test_file)
		# classify_and_eval_h(test_file)

		print "--- Test on the complete log"
		os.system("cp " + fname + " " + test_file)
		classify_and_eval_h(test_file)

		append_results()

	finally:
		os.remove(fname)
