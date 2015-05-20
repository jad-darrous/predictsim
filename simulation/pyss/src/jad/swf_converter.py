#!/usr/bin/pypy
# encoding: utf-8
'''
Convert a .swf file to feature file to be used in ML libraries.

Usage:
	swf_converter.py <swf_file> <qid> [(--indices <value> [( <value> )]...)]

Options:
	-h --help			Show this help message and exit.
	-v --verbose		Be verbose.
	-n --normalize		Normalize jobs IDs.
	-r --identical		Remove identical columns.
'''

from base.docopt import docopt
import sys
import itertools

def conv_features(fname, qid, indices=None):

	if indices is not None:
		mask = [i in indices for i in range(1, 19)]
		size = mask.count(True)
	else:
		size = 18
		mask = [True] * 18

	rng = range(1, size+1)

	score = 1000000-1;
	lines = []
	with open(fname) as f:
		for line in f:
			if not line.lstrip().startswith(';'):
				job = [int(float(u)) for u in line.strip().split()];
				l = itertools.compress(job, mask)
				t = ' '.join(map(lambda v: "%d:%d" % v, zip(rng, l)))
				lines.append("{0} qid:{1} {2}".format(score, qid, t))
				score-=1

	return '\n'.join(lines)

if __name__ == "__main__":
	
	arguments = docopt(__doc__, version='1.0.0rc2')

	print "-- SWF Converter --"

	fname = arguments["<swf_file>"]
	qid = int(arguments["<qid>"])

	ind = None
	if arguments["--indices"]:
		ind = set([int(u) for u in arguments["<value>"]])

	print conv_features(fname, qid, ind)

