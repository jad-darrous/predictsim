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

import sys
sys.path.append("..")

from base.docopt import docopt
import sys

from swf_utils import conv_features


if __name__ == "__main__":
	
	arguments = docopt(__doc__, version='1.0.0rc2')

	print "-- SWF Converter --"

	fname = arguments["<swf_file>"]
	qid = int(arguments["<qid>"])

	ind = None
	if arguments["--indices"]:
		ind = set([int(u) for u in arguments["<value>"]])

	print conv_features(fname, qid, ind)

