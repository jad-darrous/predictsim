#!/usr/bin/env python
# encoding: utf-8

'''
    extract maxprocs

Usage:
    extract_maxprocs.py <swf_file> [-h]

Options:
    -o <option>                                  some option 
    -h --help                                      show this help message and exit.
'''
from docopt import docopt
#retrieving arguments
arguments = docopt(__doc__, version='1.0.0rc2')

with open(arguments['<swf_file>']) as input_file:
    num_processors=None
    for line in input_file:
        if(line.lstrip().startswith(';')):
            if(line.lstrip().startswith('; MaxProcs:')):
                num_processors = int(line.strip()[11:])
                break
            else:
                continue
        else:
            break

print num_processors
