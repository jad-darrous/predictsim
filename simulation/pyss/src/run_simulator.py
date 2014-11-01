#!/usr/bin/pypy
# encoding: utf-8
"""
Run the PySS Simulator. You should specify a config file, an enforce input and output swfs over that via commandline if you so desire.

Usage:
    run_simulator.py <swf_file> <config_file> <output_file> [-u <usersE>] [-g] [-i] [-v]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode at key points in script.
    -g                                             if set, users are not green, else they are(-u is the user to be green or not)
"""

from base.docopt import docopt
import sys

if __debug__:
    import warnings
    #warnings.warn("Running in debug mode, this will be slow... try 'python2.4 -O %s'" % sys.argv[0])

from base.workload_parser import parse_lines
from base.prototype import _job_inputs_to_jobs
from schedulers.simulator import run_simulator
from schedulers.common import module_to_class
import optparse
import schedulers.common_correctors


def parse_and_run_simulator(options):

	if options["input_file"] is None:
		parser.error("missing input file")


	if options["input_file"] == "-":
		input_file = sys.stdin
	else:
		input_file = open(options["input_file"])

	if not options.has_key("num_processors"):
		input_file = open(options["input_file"])
		for line in input_file:
			if(line.lstrip().startswith(';')):
				if(line.lstrip().startswith('; MaxProcs:')):
					options["num_processors"] = int(line.strip()[11:])
					break
				else:
					continue
			else:
				break
	if options["num_processors"] is None:
		parser.error("missing num processors")

	if options["stats"] is None:
		options["stats"] = False

	if options["scheduler"] is None:
		parser.error("missing scheduler")

	if options["scheduler"]["name"] is None:
		parser.error("missing scheduler name")

	if not (options["usersE"] is None):
		options["usersE"] = int(options["usersE"])

	if not options.has_key('output_swf_energy'):
		options["output_swf_energy"] = False
	

	my_module = options["scheduler"]["name"]
	my_class = module_to_class(my_module)

	#load module(or file)
	package = __import__ ('schedulers', fromlist=[my_module])
	if my_module not in package.__dict__:
		print "No such scheduler (module file not found)."
		return
	if my_class not in package.__dict__[my_module].__dict__:
		print "No such scheduler (class within the module file not found)."
		return
	#load the class
	scheduler_non_instancied = package.__dict__[my_module].__dict__[my_class]

	scheduler = scheduler_non_instancied(options)


	#if hasattr(scheduler_non_instancied, 'I_NEED_A_PREDICTOR'):

	try:
		print "...."
		run_simulator(
			options = options,
			jobs = _job_inputs_to_jobs(parse_lines(input_file, options["usersE"], options["green"]), options["num_processors"]),
			scheduler = scheduler
			)

		print "Num of Processors: ", options["num_processors"]
		print "Input file: ", options["input_file"]
		print "Scheduler:", type(scheduler)

	finally:
		if input_file is not sys.stdin:
			input_file.close()


if __name__ == "__main__":
        #Retrieve arguments
        
        arguments = docopt("""
Run the PySS Simulator. You should specify a config file, an enforce input and output swfs over that via commandline if you so desire.

Usage:
    run_simulator.py <swf_file> <config_file> <output_file> [-u <usersE>] [-g] [-i] [-v]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode at key points in script.
    -g                                             if set, users are not green, else they are(-u is the user to be green or not)
""", version='1.0.0rc2')

	config = {}
	execfile(arguments["<config_file>"], config)
        config["input_file"]=arguments["<swf_file>"]
        config["output_swf"]=arguments["<output_file>"]
        config["usersE"]=arguments["<usersE>"]
        config["green"]=not arguments["-g"]
	# python 3: exec(open("example.conf").read(), config)

	parse_and_run_simulator(config)
