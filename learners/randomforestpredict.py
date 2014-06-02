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


#0-'job_id',1'submit_time',2-'wait_time',3-'run_time',4-'proc_alloc',5-'cpu_time_used',6-'mem_used',7'proc_req',8'time_req',9-'mem_req',10-'status',11'user_id',12'group_id',13-'exec_id',14-'queue_id',15-'partition_id',16-'previous_job_id',17-'think_time'.
X=np.delete(data,[0,2,3,4,5,6,9,10,13,14,15,16,17],1)
s=3600*24
X[:,0]=X[:,0] %s
i=int(len(X)*.8)
Xlearn=X[1:i:1,:]
Xtest=X[i:len(X),:]

y=data[:,4]

#interactive?
if '--interactive' in arguments.keys():
    from IPython import embed
    embed()
