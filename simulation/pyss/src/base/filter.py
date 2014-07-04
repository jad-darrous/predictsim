#!/usr/bin/env python2.4
# receives swf input on stdin, prints it back to stdout minus the lines that
# raise asserts in the simulator
import fileinput
import workload_parser
import prototype
import sys

from prototype import _job_input_to_job

for line in fileinput.input():
    if line.lstrip().startswith(';'):
        sys.stdout.write(line)
    else:
        job_input = workload_parser.JobInput(line)
        try: job = _job_input_to_job(job_input)
        except AssertionError: continue
        sys.stdout.write(line)

