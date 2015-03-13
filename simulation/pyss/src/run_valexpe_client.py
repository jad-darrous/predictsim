
import time
import multiprocessing
import fabric
from fabric.api import run
from fabric.api import env
from fabric.tasks import execute
from fabric.context_managers import cd
import os
import socket

import json

import sys
import os.path
from run_simulator import parse_and_run_simulator
import pprint
import random

from fabric.network import ssh
ssh.util.log_to_file("paramiko.log", 10)

server_path = "/home/glesser/FSE_simul/internship/simulation/pyss/src/run_valexpe_server.py"

num_threads = 24

env.use_ssh_config = True

#env.gateway = 'dglesser@stremi-6:22'
#env.hosts = ['glesser@localhost:12345']
env.hosts = ['houlette']
#env.hosts = ['localhost']
#env.key_filename = "/home/dglesser/.ssh/id_rsa.notsosecret"
#env.password = ""

my_name = str(socket.gethostname())


fabric.state.output['status'] = True
fabric.state.output['stdout'] = False
fabric.state.output['warnings'] = False
fabric.state.output['running'] = False
fabric.state.output['user'] = False
fabric.state.output['stderr'] = False
fabric.state.output['aborts'] = True
fabric.state.output['debug'] = False



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


env.use_ssh_config = True



thread_counter = multiprocessing.Value('i', 0)

expe_counter = multiprocessing.Value('i', 0)
ssh_lock = multiprocessing.Lock()


def get_expe_task():
	with cd(os.path.dirname(server_path)):
		res = run('python '+server_path+' get '+my_name)
	return res

def get_expe():
	global ssh_lock
	ssh_lock.acquire()
	res = execute(get_expe_task)
	#res = {'localhost': "(u'3', u'WAIT', u'None', u'optionssss')"}
	ssh_lock.release()

	#dont look, it's dirty
	for r in res:
		res = res[r]
		
	(a,hash,a,state,a,doer,a,options,a) = res.split("'")
	options = json.loads(options)
	print (hash,state,doer,options)
	return (hash,state,doer,options)



def expe_done_task(hash):
	with cd(os.path.dirname(server_path)):
		res = run('python '+server_path+' done '+hash)
	return res

def expe_done(hash):
	global ssh_lock
	ssh_lock.acquire()
	res = execute(expe_done_task, hash)
	ssh_lock.release()


def expe_error_task(hash):
	with cd(os.path.dirname(server_path)):
		res = run('python '+server_path+' error '+hash)
	return res

def expe_error(hash):
	global ssh_lock
	ssh_lock.acquire()
	res = execute(expe_done_task, hash)
	ssh_lock.release()
	


def launchExpe(options, worker_id):
	with expe_counter.get_lock():
		expe_counter.value += 1
		myid = expe_counter.value
	
	if not ( os.path.isfile(options["output_swf"]) ):
		print bcolors.WARNING+"Start expe "+str(myid)+" on w"+str(worker_id)+ bcolors.ENDC+" : "+str(options)
		error = False
		tempout = sys.stdout
		sys.stdout = open(options["output_swf"]+".out", 'w')
		sys.stderr = sys.stdout
		try:
			parse_and_run_simulator(options)
		except Exception,e:
			print "Exception: "+str(e)
			error = str(e)
		sys.stdout = tempout
		if not error:
			print bcolors.OKBLUE+"End   epxe "+str(myid)+ bcolors.ENDC
			return True
		else:
			print bcolors.FAIL+"ERROR on "+str(myid)+": "+str(e)+ bcolors.ENDC
			return False
	else:
		print bcolors.OKGREEN+"Already done"+str(myid)+ bcolors.ENDC+" : "+str(options)
		return True


def worker():
	global thread_counter
	with thread_counter.get_lock():
		thread_counter.value += 1
		worker_id = thread_counter.value
		print "Start Worker: ", worker_id
	try:
		while True:
			#get a new expe
			(hash,state,doer,options) = get_expe()
			
			#exec it
			#print "doing", hash
			#time.sleep(1)
			err = launchExpe(options, worker_id)
			
			#tell it ended
			if err:
				expe_error(hash)
			else:
				expe_done(hash)
	finally:
		with thread_counter.get_lock():
			thread_counter.value -= 1




def useless_task():
	print run("hostname")

#we run first a useless task to open the connection
#execute(useless_task)
#exit(0)

ts = []

for i in range(num_threads):
	t = multiprocessing.Process(target=worker)
	t.daemon = True
	t.start()
	ts.append(t)

#this:
#[x.join() for x in ts]
#do not allow keyboard interrupts,
#whereas this allow them:
while True:
	time.sleep(1)
	if thread_counter.value == 0:
		time.sleep(1)
		break;


