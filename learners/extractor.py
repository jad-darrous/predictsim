#!/usr/bin/python
'''
Job feature extractor.
This script replays a .swf file using sympy and gives, for every job, if available at submission time:
    -last known runtime of a job of this user
    -last known runtime of a job of this user (rank 2: one job before)
    -last known exit status of a job of this user
    -last known exit status of a job of this user (rank 2)
    -thinktime w.r.t. the last job sumbitted by this user. -1 if jobs are running.
    -max running length of already running jobs of this user.
    -sum of running lengths of already running jobs of this user.
    -amount of already runnnig jobs of this user.
    -average of running lengths of already running jobs of this user.
    -total currently allocated cores to this user.
CSV file format:
    job_id user_id last_runtime last_runtime2 last_status last_status2 thinktime running_maxlength running_sumlength amount_running running_average_runtime running_allocatedcores

This is under the DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE v2.0

Usage:
    extract.py <filename> [-v] [-h]

Options:
    -h --help                                      show this help message and exit.
    -v --verbose                                   print extra information and log info level data to extractor.log.
'''

__author__ = 'Valentin Reis  <valentin.reis@gmail.com>'
__version__ = '0.10'
__website__ = 'https://github.com/freuk/internship'
__license__ = 'WTFPL2.0'


import re
import logging
from collections import deque
from docopt import docopt
from simpy import Environment,simulate,Monitor
from swfpy import io
from collections import namedtuple
import numpy as np
import sys
#retrieving arguments
arguments = docopt(__doc__, version='1.0.0rc2')
#verbose?
if arguments['--verbose']==True:
    print(arguments)

#logging
global_logger = logging.getLogger('global')
hdlr = logging.FileHandler('extractor.log')
formatter = logging.Formatter('%(levelname)s %(message)s')
hdlr.setFormatter(formatter)
global_logger.addHandler(hdlr)


#logging level
if arguments['--verbose']==True:
    global_logger.setLevel(logging.INFO)
else:
    global_logger.setLevel(logging.ERROR)

#Getting a simulation environment
env = Environment()

#logging function
def global_log(msg):
    prefix='%.1f'%env.now
    global_logger.info(prefix+': '+msg)

#input
data=io.swfopen(arguments['<filename>'])

#identify user IDs
#print(data)
users=set(map(lambda j: j.user_id,data))

submitted_jobs={}
running_jobs={}
user_info={}

UserInfo= namedtuple('UserInfo', 'last_runtime last_runtime2 last_runtime3 last_runtime4 last_status last_status2 last_jobend')

for uid in users:
    submitted_jobs[uid]=[]
    running_jobs[uid]=[]
    #user_info[uid]['UserInfo'](-1,-1,-1,-1,-1)
    user_info[uid]={'last_runtime':-1, 'last_runtime2':-1, 'last_runtime3':-1, 'last_runtime4':-1, 'last_status':-1, 'last_status2':-1, 'last_jobend':-1,'last_submit':data[0].submit_time}

def job_submit(j):
    log=lambda x: global_log("JOB SUBMIT: "+x)
    log("entering job_sumbit with job %s" %(j,))
    submitted_jobs[j.user_id].append(j)
    log("dbg1")
    #dataoutput for job j, including thinktime computation
    #job_id user_id last_runtime last_runtime2 last_runtime3 last_runtime4 last_status last_status2 thinktime running_maxlength running_sumlength amount_running running_average_runtime running_allocatedcores
    printlist=[j.job_id,j.user_id,user_info[j.user_id]['last_runtime'],user_info[j.user_id]['last_runtime2'],user_info[j.user_id]['last_runtime4'],user_info[j.user_id]['last_status'],user_info[j.user_id]['last_status2']]
    log("dbg2")

    if user_info[j.user_id]['last_jobend']>=0:
        log("dbg2.1")
        printlist.append(env.now-user_info[j.user_id]['last_jobend'])
        log("dbg2.3")
        user_info[j.user_id]['last_jobend']=-1
    else:
        log("dbg2.2")
        printlist.append(-1)
    log("dbg3")

    amount_running=len(running_jobs[j.user_id])
    if amount_running>0:
        running_maxlength=max([env.now-j2.submit_time-j2.wait_time for j2 in running_jobs[j.user_id]])
        running_sumlength=sum([env.now-j2.submit_time-j2.wait_time for j in running_jobs[j.user_id]])
        running_average_runtime=np.average([env.now-j2.submit_time-j2.wait_time for j in running_jobs[j.user_id]])
        running_allocatedcores=sum([abs(j2.proc_alloc) for j2 in running_jobs[j.user_id]])
    else:
        running_maxlength=0
        running_sumlength=0
        running_average_runtime=0
        running_allocatedcores=0

    running_totalcores=sum([sum([abs(j2.proc_alloc) for j2 in running_jobs[uidvar]]) for uidvar in users])

    log("dbg4")
    printlist.append(running_maxlength)
    printlist.append(running_sumlength)
    printlist.append(amount_running)
    printlist.append(running_average_runtime)
    printlist.append(running_allocatedcores)
    printlist.append(env.now-user_info[j.user_id]['last_submit'])
    printlist.append(running_totalcores)
    printlist.append(user_info[j.user_id]['last_runtime3'])
    printlist.append(user_info[j.user_id]['last_runtime4'])

    s=""
    for e in printlist:
        s+=str(e)+" "
    print(s)
    log("dbg5")

    #print(j.job_id)

def job_start(j):
    log=lambda x: global_log("JOB START: "+x)
    log("entering job_start")
    running_jobs[j.user_id].append(j)

def job_end(j):
    log=lambda x: global_log("JOB END: "+x)
    log("entering job_end")
    running_jobs[j.user_id].remove(j)
    submitted_jobs[j.user_id].append(j)
    #modify data for this user
    user_info[j.user_id]['last_runtime4']=user_info[j.user_id]['last_runtime3']
    user_info[j.user_id]['last_runtime3']=user_info[j.user_id]['last_runtime2']
    user_info[j.user_id]['last_runtime2']=user_info[j.user_id]['last_runtime']
    user_info[j.user_id]['last_runtime']=j.run_time
    user_info[j.user_id]['last_status2']=user_info[j.user_id]['last_status']
    user_info[j.user_id]['last_status']=j.status
    #including : think about the last_jobend
    if len(running_jobs[j.user_id])==0:
        user_info[j.user_id]['last_jobend']=env.now

def job_process(j):
    job_submit(j)
    yield env.timeout(j.wait_time)
    job_start(j)
    yield env.timeout(j.run_time)
    job_end(j)

from simpy.util import start_delayed
for j in data:
    start_delayed(env,job_process(j),j.submit_time)

#TODO:DEL dataframe

#print(users)
#for user in users:
    #print("User %s with %s campaigns:" %(user.uid,len(user.campaign_deque)))
    #for campaign in user.campaign_deque:
        #print(campaign)
        #for job in campaign.jobs:
            #print(job)

#if arguments['--verbose'] == True:
    #system.set_monitor(system_monitor(system,env,FileBackend(env,'csim_system.log')))
    #ubackend=FileBackend(env,'csim_users.log')
    #for u in users:
        #u.set_monitor(user_monitor(u,env,ubackend))
#cronjob_progression = Cronjob_progression(env,cronfreq,users,'csim_usersummary.log')
#cronjob_progression.start()

#def terminator():
    #log('TERMINATOR : waiting for all users to finish.')
    #yield simpy.util.all_of([u.over for u in users])
    #system.stop()
    #cronjob_progression.stop()
    #log('TERMINATOR : all users finished.')
#env.start(terminator())

#sys.setrecursionlimit(20000)
simulate(env)

print('-------------SUCCESS----------------')
