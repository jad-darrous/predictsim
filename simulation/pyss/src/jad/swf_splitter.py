#!/usr/bin/pypy
# encoding: utf-8
'''
Split a .swf file into multiple parts.

Usage:
	swf_splitter.py <swf_file> <tpercent> <parts> [<dir>]

Options:
	-h --help			Show this help message and exit.
	-v --verbose		Be verbose.
	-n --normalize		Normalize jobs IDs.
	-r --identical		Remove identical columns.
'''

from base.docopt import docopt
import sys

def split_swf(in_file_name, tpercent, parts, dir="./"):

	def write_to_file(fname, jobs):
		out = open(fname, "w")
		out.write('\n'.join(jobs));
		out.close()

	info = []
	jobs = []
	with open(in_file_name) as f:
		for line in f:
			if not line.lstrip().startswith(';'):
				jobs.append(line.strip());
			else:
				info.append(line.strip().split(';')[1])

	training_size = int(len(jobs) * tpercent)
	part_size = training_size / parts

	str_name_format = "%s/%s_part%%d.swf" % (dir, in_file_name.split('.')[0])

	training_files = []

	for i in range(parts):
		fname = str_name_format % (i+1)
		training_files.append(fname)
		write_to_file(fname, jobs[i*part_size:(i+1)*part_size])

	test_file = "%s/%s_test.swf" % (dir, in_file_name.split('.')[0])
	write_to_file(test_file, jobs[training_size:])

	return training_files, test_file

if __name__ == "__main__":

	arguments = docopt(__doc__, version='1.0.0rc2')

	print "-- SWF Splitter --"

	if not arguments["<parts>"].isdigit():
		raise KeyError(arguments["<parts>"] + " is not an integer")

	split_swf(arguments["<swf_file>"], float(arguments["<tpercent>"]), int(arguments["<parts>"]), 'output')

	print "Splitting done for file:", arguments["<swf_file>"]
