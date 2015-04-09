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

from datetime import timedelta
import os
import gc


weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0), (0, 0, 0, 0, 0, +1)]
#weights_options = [(1, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0), (0, 0, 0, 0, 0, +1), (0, 0, 0, 0, 0, -1)]
# weights_options = [(1, 0, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0, 0), (0, 0, 1, 0, 0, 0, 0), (0, 0, 0, 0, 0, +1, 0), (0, 0, 0, 0, 0, -1, 0)]

training_percentage = 0.6;
training_parts = 4;

indices = (2,3,4,5,11)

train_fn = 'train.txt'
test_fn = 'test.txt'
model_fn = 'model.txt'
cl_out_fn = 'cl_out.txt' # classification's output file
new_l2r_fn = 'new_l2r.txt' # this file contains the jobs after reordering/adding think time

train_log_fn = 'svm_rank_learn.log'
classify_log_fn = 'svm_rank_classify.log'

out_dir = "output"

rel = lambda fn: "%s/%s" % (out_dir, fn);


def write_str_to_file(fname, _str):
	with open(fname, "w") as f:
		f.write(_str)
		# assert f.write(_str) == len(_str)

def write_lines_to_file(fname, lines):
	write_str_to_file(fname, '\n'.join(lines))

def reorder_jobs(infile, outfile, criteria):

	jobs = []
	with open(infile) as f:
		for line in f:
			if not line.lstrip().startswith(';'):
				jobs.append(line.strip());

	new_jobs = []
	for i in criteria:
		new_jobs.append(jobs[i])

	write_lines_to_file(outfile, new_jobs)


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


def average_stretch_time(fname):

	# time.sleep(1)
	# with open(fname) as f, open("dd.txt", "w") as o:
	# 	o.write(f.read())
	# print fname
	# return 0;
	s_time = []
	with open(fname, "rb") as f:
		for line in f.xreadlines():
			if not line.lstrip().startswith(';'):
				# print line.lstrip()
				try:
					wt, rt = [float(v) for v in [u for u in line.strip().split()][2:4]]
					s_time.append((wt+rt)/rt);
				except :
					print 'except'
					pass
	return sum(s_time) / len(s_time)


if __name__ == "__main__":

	arguments = docopt(__doc__, version='1.0.0rc2')

	# test_file = 'output/log_test.swf'

	# # add the l2r to the test log as the think time.
	# l = [float(u) for u in open("%s/%s" % (out_dir, cl_out_fn))]
	# h = "%s/%s" % (out_dir, new_l2r_fn)
	# add_l2r_score_jobs(test_file, h, l)
	
	# config = {
	# 	"scheduler": {"name":'maui_scheduler'},
	# 	"num_processors": 80640,
	# 	"stats": False,
	# 	"verbose": False
	# }

	# # Simulate the file after l2r
	# config["scheduler"]["name"] = 'l2r_maui_scheduler'
	# config["weights"] = (0, 0, 0, 0, 0, 0, 1)
	# config["input_file"] = test_file
	# config["output_swf"] = "%s_sim_l2r.swf" % h.split('.')[0]
	# l2r_exc_time = parse_and_run_simulator(config)
	# print "l2r_exc_time:", l2r_exc_time

	# print average_stretch_time(rel("log_part1.swf"))
	
	# import progressbar
	# widgets = ['# Jobs Terminated: ', progressbar.Counter(),' ',progressbar.Timer()]
	# pbar = progressbar.ProgressBar(widgets=widgets,maxval=10000000, poll=0.1).start()
	# for i in range(1000000):
	# 	pbar.update(i)
	# exit(0)

	os.system("date")
	os.system("rm %s/*" % out_dir)

	config = {
		"scheduler": {"name":'maui_scheduler', "progressbar": False},
		"num_processors": 80640,
		"stats": False,
		"verbose": False
	}

	fname = arguments["<swf_file>"]

	out_files, test_file = split_swf(fname, training_percentage, training_parts, dir=out_dir)

	best_all = []
	for p in out_files:
		index, best, outf = None, float("inf"), None
		out_swf = []
		for idx, w in enumerate(weights_options):
			config["weights"] = w
			config["input_file"] = p
			config["output_swf"] = "%s_%d.swf" % (p.split('.')[0], idx)
			exc_time = parse_and_run_simulator(config)
			out_swf.append(config["output_swf"])

		gc.collect()

		for idx, swf in enumerate(out_swf):
			# exc_time_ms = exc_time.total_seconds()
			exc_time_ms = average_stretch_time(swf)
			if exc_time_ms < best:
				best = exc_time_ms
				index = idx
				outf = swf
		best_all.append(outf)
		print index, best


	print "[Converting swf file format to ML file format..]"
	features = []
	for idx, f in enumerate(best_all):
		features.append(conv_features(f, idx, indices))
	write_lines_to_file(rel(train_fn), features)

	features = conv_features(test_file, 0, indices)
	write_str_to_file(rel(test_fn), features)

	print "[Training..]"
	os.system("./svm_rank_learn -c 3 {0}/{1} {0}/{2} > {0}/{3}". \
		format(out_dir, train_fn, model_fn, train_log_fn))

	print "[Classifying/Testing..]"
	os.system("./svm_rank_classify -v 3 {0}/{1} {0}/{2} {0}/{3} > {0}/{4}". \
		format(out_dir, test_fn, model_fn, cl_out_fn, classify_log_fn))


	print "[Simulating the test file..]"
	# Simulate the test file
	index, best, run_time = None, float("inf"), None
	out_swf = []
	for idx, w in enumerate(weights_options):
		config["weights"] = w
		config["input_file"] = test_file
		config["output_swf"] = "%s_sim%d.swf" % (test_file.split('.')[0], idx)
		exc_time = parse_and_run_simulator(config)
		# exc_time_ms = exc_time.total_seconds()
		out_swf.append(config["output_swf"])

		# gc.collect()

		# exc_time_ms = average_stretch_time(config["output_swf"])
		# print exc_time_ms
		# if exc_time_ms < best:
		# 	best = exc_time_ms
		# 	index = idx

	gc.collect()
	# print "test_exc_time:", best
	# print map(lambda u: average_stretch_time(u), out_swf)
	best = min(map(lambda u: average_stretch_time(u), out_swf))
	print "test_exc_time:", best


	# # reorder the jobs according to their score
	# l = [float(u) for u in open("%s/%s" % (out_dir, cl_out_fn))]
	# x = zip(l, range(len(l)))
	# z = sorted(x, key=lambda v: v[0])
	# o = map(lambda u: u[1], z)
	# h = "%s/%s" % (out_dir, new_l2r_fn)
	# reorder_jobs(test_file, h, o)

	# # Simulate the file after l2r
	# config["weights"] = weights_options[0]
	# config["input_file"] = h
	# config["output_swf"] = "%s_sim.swf" % h.split('.')[0]
	# l2r_exc_time = parse_and_run_simulator(config)
	# print "l2r_exc_time:", l2r_exc_time

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
	l2r_exc_time = parse_and_run_simulator(config)
	l2r_exc_time = average_stretch_time(config["output_swf"])
	print "l2r_exc_time:", l2r_exc_time
