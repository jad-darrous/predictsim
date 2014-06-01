#!/usr/bin/env python
# encoding: utf-8
'''
#!/usr/bin/python
random forest predictor.
DWTFPL v2.0

Usage:
    meanpredict.py <filename> [-i] [-v]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode after script.

    Please format the csv file correctly before using: remove comments! Fields should be: 'job_id','submit_time','wait_time','run_time','proc_alloc','cpu_time_used','mem_used','proc_req','time_req','mem_req','status','user_id','group_id','exec_id','queue_id','partition_id','previous_job_id','think_time'.
'''
from docopt import docopt
#retrieving arguments
arguments = docopt(__doc__, version='1.0.0rc2')

#verbose?
if '--verbose' in arguments.keys():
    print(arguments)



import numpy as np
from swfpy import io
data=io.swfopen(arguments["<filename>"],output="np.array")
#print data

data
data=data.view(np.int32).reshape(data.shape + (-1,))
#TODO: hour of day, day of week.
#subtime=np.

np.delete(data,0,1)


#interactive?
if '--interactive' in arguments.keys():
    from IPython import embed
    embed()
