#!/usr/bin/pypy
# encoding: utf-8
'''
Main script that combine everyting.

Usage:
	run.py <swf_file>

Options:
	-h --help			Show this help message and exit.
	-v --verbose		Be verbose.
'''

import sys
sys.path.append("..")

from base.docopt import docopt

from run_simulator import parse_and_run_simulator
from swf_splitter import split_swf
from swf_converter import conv_features

from batch_learning_to_rank import SVM_Rank, RankLib

from datetime import timedelta
import os
import gc


train_fn = 'train.txt'
test_fn = 'test.txt'
model_fn = 'model.txt'
cl_out_fn = 'cl_out.txt' # classification's output file
new_l2r_fn = 'new_l2r.txt' # this file contains the jobs after reordering/adding think time


out_dir = "output"

rel = lambda fn: "%s/%s" % (out_dir, fn);



def write_str_to_file(fname, _str):
	with open(fname, "w") as f:
		f.write(_str)
		# assert f.write(_str) == len(_str)

def write_lines_to_file(fname, lines):
	write_str_to_file(fname, '\n'.join(lines))


def add_l2r_score_jobs(infile, outfile, score):

	jobs = []
	with open(infile) as input_file:
		c = 0
		for line in input_file:
			if not line.lstrip().startswith(';'):
				job = [u for u in line.strip().split()]
				jobs.append(' '.join(job[:-1] + [str(int(score[c] * 1000))]));
				c += 1

	write_lines_to_file(outfile, jobs)


def stretch(wt, rt):
	return (wt+rt)/rt

def bounded_slowdown(wt, rt):
	tau = 10.0
	return max((wt+rt)/max(rt, tau), 1)

def average_func(fname, func):

	s_time = []
	with open(fname, "rb") as f:
		for line in f.xreadlines():
			if not line.lstrip().startswith(';'):
				try:
					wt, rt = [float(v) for v in [u for u in line.strip().split()][2:4]]
					s_time.append(func(wt, rt));
				except:
					print 'except'
					pass
	return sum(s_time) / len(s_time)

def average_stretch(fname):
	return average_func(fname, stretch)

def average_bounded_slowdown(fname):
	return average_func(fname, bounded_slowdown)


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
the training parts then select the best part for each scheduler's
configuration and then prepare the training file of features to
be fed to the learning algorithm and returns the test file name
"""
def split_and_simulate(fname):

	os.system("rm -f %s/*" % out_dir)

	out_files, test_file = split_swf(fname, training_percentage, training_parts, dir=out_dir)

	print "[Simulating the training set..]"

	best_all = []
	for p in out_files:
		index, best, outf = None, float("inf"), None
		out_swf = simulate(p)

		gc.collect()

		for idx, swf in enumerate(out_swf):
			avg_stch = obj_func(swf)
			if avg_stch < best:
				best = avg_stch
				index = idx
				outf = swf

		best_all.append(outf)
		print index, best


	print "[Creating the ML training file..]"
	features = []
	for idx, f in enumerate(best_all):
		features.append(conv_features(f, idx, indices))
	write_lines_to_file(rel(train_fn), features)

	return test_file


def training():
	print "[Training..]"
	batchL2Rlib.train(train_fn, model_fn)


def classify_and_eval_h(test_file):

	print "[Creating the ML testing file..]"
	features = conv_features(test_file, 0, indices)
	write_str_to_file(rel(test_fn), features)

	print "[Simulating the test file..]"
	# Simulate the test file
	out_swf = simulate(test_file)
	gc.collect()
	best_std_obj_func_val = min(map(lambda u: obj_func(u), out_swf))
	print "+ Bounded-Slowdown [Std]:", best_std_obj_func_val


	print "[Classifying/Testing..]"
	batchL2Rlib.classify(test_fn, model_fn, cl_out_fn)

	print "[Simulating the test file using L2R..]"
	# add the l2r to the test log as the think time.
	score = [float(u) for u in open(rel(cl_out_fn))]
	test_l2r_fn = rel(new_l2r_fn)
	add_l2r_score_jobs(test_file, test_l2r_fn, score)

	# Simulate the file after l2r
	config["scheduler"]["name"] = 'l2r_maui_scheduler'
	config["weights"] = (0, 0, 0, 0, 0, 0, 1)
	config["input_file"] = test_l2r_fn
	config["output_swf"] = "%s_sim_l2r.swf" % test_l2r_fn.split('.')[0]
	parse_and_run_simulator(config)
	l2r_obj_func_val = obj_func(config["output_swf"])
	print "+ Bounded-Slowdown [L2R]:", l2r_obj_func_val

	res_data.append(str(best_std_obj_func_val))
	res_data.append(str(l2r_obj_func_val))


obj_func = average_stretch
obj_func = average_bounded_slowdown

batchL2Rlib = SVM_Rank(out_dir)


def getMaxProcs(fname):
	with open(fname) as f:
		for line in f.readlines():
			if "; MaxProcs:" in line:
				return int(line.strip().split()[-1])
	raise NameError('No MaxProcs in the log')


res_data = []
def append_results():
	with open("results/results.txt", "a") as myfile:
	    myfile.write(' '.join(res_data) + '\n')


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

	res_data.append(fname)

	execfile("conf.py")
	
	config["num_processors"] = getMaxProcs(log_path)

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
		print "--- Test on the complete log"
		os.system("cp " + fname + " " + test_file)
		classify_and_eval_h(test_file)

		append_results()

	finally:
		os.remove(fname)
