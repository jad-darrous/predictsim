#!/usr/bin/python
'''
Job feature extractor.
This script replays a .swf file using sympy and gives, for every job, if available at submission time:
    -last known runtime of a job of this user
    -last known runtime of a job of this user (rank 2: one job before)
    -last known exit status of a job of this user
    -last known exit status of a job of this user (rank 2)
    -thinktime w.r.t. the last job sumbitted by this user. may be negative.
CSV file format:
    job_id lastruntime lastruntime_2 laststatus laststatus_2 thinktime

This is under the DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE v2.0

Usage:
    extract.py <filename> [-v] [-h]

Options:
    -h --help                                      show this help message and exit.
    -v --verbose                                   print extra information and log info level data to extractor.log.
'''
#External tool import
import logging
import re
from collections import deque
from docopt import docopt
from simpy import Environment,simulate,Monitor
from simpy.monitoring import PrinterBackend
#debug
#import pdb
#our files import

#retrieving arguments
arguments = docopt(__doc__, version='1.0.0rc2')
print(arguments)

#verbose?
if arguments['--verbose']==True:
    print(arguments)

#Getting a simulation environment
env = Environment()

#logger:
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

#logging function
def log(msg):
    prefix='%.1f'%env.now
    global_logger.info(prefix+': '+msg)

#input


#users
users=[]
for uid in yusers.keys():
    job_deque=deque()
    for c in yusers[uid]:
        job_deque.append(Job("truc"))#TODO
    users.append(User(env,uid,campaign_deque,system,log))

#TODO:DEL dataflame

#print(users)
#for user in users:
    #print("User %s with %s campaigns:" %(user.uid,len(user.campaign_deque)))
    #for campaign in user.campaign_deque:
        #print(campaign)
        #for job in campaign.jobs:
            #print(job)

f= open(arguments['<output>'],'w+')

system.start()
for user in users:
    user.start(f)

#TODO: lasuite!!!
if arguments['--verbose'] == True:
    system.set_monitor(system_monitor(system,env,FileBackend(env,'csim_system.log')))
    ubackend=FileBackend(env,'csim_users.log')
    for u in users:
        u.set_monitor(user_monitor(u,env,ubackend))
cronjob_progression = Cronjob_progression(env,cronfreq,users,'csim_usersummary.log')
cronjob_progression.start()

def terminator():
    log('TERMINATOR : waiting for all users to finish.')
    yield simpy.util.all_of([u.over for u in users])
    system.stop()
    cronjob_progression.stop()
    log('TERMINATOR : all users finished.')
env.start(terminator())

simulate(env)

f.close()

print('-------------SUCCESS----------------')
