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
import re
from collections import deque
from docopt import docopt
from simpy import Environment,simulate,Monitor
from swfpy import io
from collections import namedtuple
import numpy as np
#retrieving arguments
arguments = docopt(__doc__, version='1.0.0rc2')
print(arguments)
#verbose?
if arguments['--verbose']==True:
    print(arguments)

#input
data=io.swfopen(arguments["<filename>"])

#Getting a simulation environment
env = Environment()

#identify user IDs
users=set(map(lambda j: j.user_id,data))

submitted_jobs={}
running_jobs={}
user_info={}

UserInfo= namedtuple('UserInfo', 'last_runtime last_runtime2 last_status last_status2 last_jobend')
RunningJob = namedtuple('RunningJob', 'job_id start_time cores')

for uid in users:
    submitted_jobs[uid]=[]
    running_jobs[uid]=[]
    user_info[uid]=UserInfo(-1,-1,-1,-1,-1)

def job_submit(j):
    submitted_jobs[j.user_id].append(j)
    #dataoutput for job j, including thinktime computation
    #job_id user_id last_runtime last_runtime2 last_status last_status2 thinktime running_maxlength running_sumlength amount_running running_average_runtime running_allocatedcores
    printlist=[j.job_id,j.user_id,user_info[j.user_id].last_runtime,user_info[j.user_id].last_runtime2,user_info[j.user_id].last_status,user_info[j.user_id].last_status2]

    if user_info[uid].last_jobend>=0:
        printlist+=env.now-user_info[uid].last_jobend
        user_info[uid].last_jobend=-1
    else:
        printlist+=-1

    amount_running=len(running_jobs[uid])
    if amount_running>0:
        running_maxlength=max([env.now-j.submit_time-j.wait_time for j in running_jobs[uid]])
        running_sumlength=sum([env.now-j.submit_time-j.wait_time for j in running_jobs[uid]])
        running_average_runtime=np.average([env.now-j.submit_time-j.wait_time for j in running_jobs[uid]])
        running_allocatedcores=sum([abs(j.proc_alloc) for j in running_jobs[uid]])
    else:
        running_maxlength=0
        running_sumlength=0
        running_average_runtime=0
        running_allocatedcores=0

    s+=running_maxlength
    s+=running_sumlength
    s+=amount_running
    s+=running_average_runtime
    s+=running_allocatedcores

    s=""
    for e in printlist:
        s+=str(e)+" "
    print(e)



def job_start(j):
    running_jobs[j.user_id].append(j)

def job_end(j):
    running_jobs[j.user_id].remove(j)
    submitted_jobs[j.user_id].remove(j)
    #modify data for this user
    user_info[uid].last_runtime2=user_info[uid].last_runtime
    user_info[uid].last_runtime=j.run_time
    user_info[uid].last_status2=user_info[uid].last_status
    user_info[uid].last_status=j.status
    #including : think about the last_jobend
    if len(running_jobs[j.user_id])==0:
        user_info[uid].last_jobend=env.now


def job_start(j):
    yield env.timeout(j.submit_time)
    job_submit(j)
    yield env.timeout(j.wait_time)
    job_start(j)
    yield env.timeout(j.run_time)
    job_end(j)

for j in data:
    env.start(job_start(j))

CommonUsers=[]
for uid in users:
    users.append(Common.User(env,uid,userdeques[uid],system,log))

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

simulate(env)

print('-------------SUCCESS----------------')
