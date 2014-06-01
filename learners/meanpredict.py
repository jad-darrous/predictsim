#!/usr/bin/env python
# encoding: utf-8
'''

#!/usr/bin/python
Tsafir et al "mean of last 2 runtimes" runtime predictor.
DWTFPL v2.0

Usage:
    meanpredict.py <filename>

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.

    Please format the csv file correctly before using: remove comments! Fields should be: 'job_id','submit_time','wait_time','run_time','proc_alloc','cpu_time_used','mem_used','proc_req','time_req','mem_req','status','user_id','group_id','exec_id','queue_id','partition_id','previous_job_id','think_time'.
'''
from docopt import docopt
#retrieving arguments
arguments = docopt(__doc__, version='1.0.0rc2')
print(arguments)

#verbose?
if '--verbose' in arguments.keys():
    print(arguments)

from swfpy import io

data=io.swfopen(arguments["<filename>"])

users=set(map(lambda j: j.user_id,data))

pastruntime1={}
pastruntime2={}
for uid in users:
    pastruntime1[uid]=-1
    pastruntime2[uid]=-1

predictions=[]
for job in data:
    uid=job.user_id
    r1=pastruntime1[uid]
    r2=pastruntime2[uid]
    if not r1==-1 and not r2==-1:
      pred=(r1+r2)/2
      print str(job.job_id)+" "+str(job.run_time)+" "+str(pred)
    else:
      print str(job.job_id)+" "+str(job.run_time)+" "+str(job.time_req)
    pastruntime1[uid]=pastruntime2[uid]
    pastruntime2[uid]=job.run_time
