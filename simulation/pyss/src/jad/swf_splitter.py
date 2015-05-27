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

import sys
sys.path.append("..")

from base.docopt import docopt
import sys

from swf_utils import split_swf


if __name__ == "__main__":

	arguments = docopt(__doc__, version='1.0.0rc2')

	print "-- SWF Splitter --"

	if not arguments["<parts>"].isdigit():
		raise KeyError(arguments["<parts>"] + " is not an integer")

	tpercent = float(arguments["<tpercent>"])
	parts = int(arguments["<parts>"])
	out_dir = 'output' if arguments["<dir>"] is None else arguments["<dir>"]

	split_swf(arguments["<swf_file>"], tpercent, parts, out_dir)

	print "Splitting done for file:", arguments["<swf_file>"]
