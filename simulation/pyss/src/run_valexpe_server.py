#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys
import sqlite3
import hashlib
import os
import time


expe_name = "KTH-SP2"
num_processors = 100
expe_dir = "../../../experiments/data/"+expe_name
conn = sqlite3.connect(expe_dir+"/run.db", timeout=120)
ouput_dir = expe_dir+"/simulations/"
input_file = expe_dir+"/swf/log.swf"

dict_path = '../../../experiments/experiment_dicts.py'
dict_path = '../../../experiments/experiment_dicts_kth.py'


def nice(s):
	# transform an dict into something command-line compatible, the ugliest way!
	return str(s).translate(None, " ':/(){},\"").replace("name", "").replace("predictor_sgdlinear", "gdl").replace("max_coresauto", "").replace("regularizationl2", "").replace("lambda4000000000", "").replace("gdNAG", "")


def hash(s):
	return hashlib.sha1(nice(s)).hexdigest()
	

def db_init_new_db():
	
	exec(open(dict_path).read())
	configs=[
		{
		'input_file': input_file,
		"num_processors":num_processors,
		'output_swf': ouput_dir+"res_"+s["name"]+"_"+nice(s["predictor"])+"_"+nice(s["corrector"])+".swf.gz",
		'stats': False,
		"scheduler":s
		}
		for s in sched_configs]
	
	
	c = conn.cursor()

	# Create table
	c.execute('''CREATE TABLE expes (hash text, state text, doer text, options text)''')

	# Insert a row of data
	for conf in configs:
		c.execute("INSERT INTO expes VALUES (?, 'WAIT', 'None', ?)", (hash(conf), json.dumps(conf)))

	# Save (commit) the changes
	conn.commit()
	

def db_init_new_db_dir():
	
	exec(open(dict_path).read())
	nconf = len(sched_configs)
	nconf_skipped = 0
	nconf_finished = 0
	configs=[]
	for s in sched_configs:
		output_swf = ouput_dir+"res_"+s["name"]+"_"+nice(s["predictor"])+"_"+nice(s["corrector"])+".swf.gz"
		if os.path.isfile(output_swf) :
			wrong = True
			for line in open(output_swf+".out"):
				if "Traceback" in line:
					break
				if "Exception" in line:
					break
				if "Elapsed Time" in line:
					wrong = False
					break
			if wrong:
				print "rm", output_swf
				print "rm", output_swf+".out"
				nconf_skipped += 1
			else:
				nconf_finished += 1
				continue
		configs.append({
			'input_file': input_file,
			"num_processors":num_processors,
			'output_swf': output_swf,
			'stats': False,
			"scheduler":s
			})
	print nconf, "expes =", len(configs), "todo +", nconf_skipped, "in error +", nconf_finished, "finished"

	c = conn.cursor()

	# Create table
	c.execute('''CREATE TABLE expes (hash text, state text, doer text, options text)''')

	# Insert a row of data
	for conf in configs:
		c.execute("INSERT INTO expes VALUES (?, 'WAIT', 'None', ?)", (hash(conf), json.dumps(conf)))

	# Save (commit) the changes
	conn.commit()


def db_init_new_db_dumb():
	c = conn.cursor()

	# Create table
	c.execute('''CREATE TABLE expes (hash text, state text, doer text, options text)''')

	# Insert a row of data
	c.execute("INSERT INTO expes VALUES ('1','WAIT', 'None', 'optionssss')")
	c.execute("INSERT INTO expes VALUES ('2','WAIT', 'None', 'optionssss')")
	c.execute("INSERT INTO expes VALUES ('3','WAIT', 'None', 'optionssss')")

	# Save (commit) the changes
	conn.commit()


def action_get(doer):
	c = conn.cursor()
	c.execute('SELECT * FROM expes WHERE state = "WAIT" ORDER BY hash LIMIT 1')
	expe = c.fetchone()
	print(expe)
	
	c.execute('UPDATE expes SET state="DOING", doer=? WHERE hash=?', (doer,expe[0]))
	
	# Save (commit) the changes
	conn.commit()
	


def update_hash_doing(expe_h, status):
	c = conn.cursor()
	c.execute('SELECT * FROM expes WHERE hash=?', (expe_h,))
	expe = c.fetchone()
	print(expe)
	
	if expe[1] != u'DOING':
		print("ERROR: This expe is not DOING (s: %s)" % expe[1])
		return
	
	c.execute('UPDATE expes SET state=? WHERE hash=?', (status,expe_h))
	
	
	# Save (commit) the changes
	conn.commit()



def action_done(expe_h):
	update_hash_doing(expe_h, u'DONE')


def action_error(expe_h):
	update_hash_doing(expe_h, u'ERROR')


def action_print(id=None):
	c = conn.cursor()
	count = 0
	sql = 'SELECT * FROM expes'
	if id != None:
		sql += ' WHERE hash="'+ str(id)+'"'
	sql += ' ORDER BY hash'
	for row in c.execute(sql):
		print row
		count += 1
	print "Number of entries:", count



def floatToTime(t):
	return time.strftime("%H:%M:%S", time.gmtime(t))

def action_stats():
	import numpy as np
	import re
	printf = sys.stdout.write
	
	exec(open(dict_path).read())
	nconf = len(sched_configs)
	nconf_skipped = 0
	nconf_finished = 0
	summ = 0
	mini = 99999999
	maxi = 0
	data = []
	configs=[]
	for s in sched_configs:
		output_swf = ouput_dir+"res_"+s["name"]+"_"+nice(s["predictor"])+"_"+nice(s["corrector"])+".swf.gz"
		if os.path.isfile(output_swf+".out") :
			wrong = True
			for line in open(output_swf+".out"):
				if "Traceback" in line:
					break
				if "Exception" in line:
					break
				if "Elapsed Time" in line:
					a = re.findall('([0-9]+):([0-9]+):([0-9]+.[0-9]+)', line)
					#print a
					sec = float(a[0][2])
					minu = float(a[0][1])
					hour = float(a[0][0])
					t = sec + minu*60 + hour*3600
					#print line, t
					summ += t
					mini = min(t, mini)
					maxi = max(t, maxi)
					data += [t]
					wrong = False
					break
			if wrong:
				nconf_skipped += 1
			else:
				nconf_finished += 1
				continue
		configs.append({
			'input_file': input_file,
			"num_processors":num_processors,
			'output_swf': output_swf,
			'stats': False,
			"scheduler":s
			})
		

	n = nconf_finished
	if n != 0:
		print "min: ",floatToTime(mini), "  ave: ",floatToTime(summ/n), "  max: ",floatToTime(maxi), "  n:", n

		histo = np.histogram(data, bins=[0,10*60,40*60,1.5*3600,3*3600,6*3600,12*3600,25*3600,999*3600])
		histo_range = max(histo[0])
		n_ticks = 50
		for i in range(len(histo[0])):
			printf( "[" + floatToTime(histo[1][i]) + ", "+ floatToTime(histo[1][i+1])+ ") ")
			printf(str(histo[0][i])+"\t")
			printf("|")
			for tick in range(int( histo[0][i] * n_ticks / histo_range)):
				printf("∎")
			printf('\n')
	print nconf, "expes =", len(configs), "todo +", nconf_skipped, "in error +", nconf_finished, "finished"


def action_stats_db():
	c = conn.cursor()
	
	count = len(c.execute('SELECT * FROM expes WHERE state="WAIT"').fetchall())
	print "Wait:", count
	count = len(c.execute('SELECT * FROM expes WHERE state="DONE"').fetchall())
	print "Done:", count
	count = len(c.execute('SELECT * FROM expes WHERE state="ERROR"').fetchall())
	print "Error:", count
	count = len(c.execute('SELECT * FROM expes WHERE state="DOING"').fetchall())
	print "Doing:", count



def action_copy():
	printf = sys.stdout.write
	
	exec(open(dict_path).read())
	
	ncopy = 0
	nerror = 0
	nunkn = 0
	
	for s in sched_configs:
		output_swf = ouput_dir+"res_"+s["name"]+"_"+nice(s["predictor"])+"_"+nice(s["corrector"])+".swf.gz"
		if os.path.isfile(output_swf) :
			state = "UNKNOWN"
			for line in open(output_swf+".out"):
				if "Traceback" in line:
					state = "ERROR"
					break
				if "Exception" in line:
					state = "ERROR"
					break
				if "Elapsed Time" in line:
					state = "DONE"
					break
			if state == "ERROR":
				print "rm", output_swf
				print "rm", output_swf+".out"
				nerror += 1
			elif state == "DONE":
				cmd = "rsync -avz --remove-source-files -e 'ssh -p 12345' "+output_swf+" glesser@localhost:/home/glesser/FSE_simul/internship/experiments/data/"+expe_name+"/simulations/"
				print cmd
				os.system(cmd)
				cmd = "rsync -avz -e 'ssh -p 12345' "+output_swf+".out"+" glesser@localhost:/home/glesser/FSE_simul/internship/experiments/data/"+expe_name+"/simulations/"
				print cmd
				os.system(cmd)
				ncopy += 1
			else:
				#print 'nano "'+output_swf+".out"+'"'
				nunkn += 1
	print "Copied:", ncopy, " // Error:", nerror, " // Unknwown:", nunkn




def action_check_db(reset=False):
	c = conn.cursor()
	expes = c.execute('SELECT * FROM expes').fetchall()
	for expedb in expes:
		options = json.loads(expedb[3])
		output_swf = options["output_swf"]
		new_state = "UNKNOWN"
		if not os.path.isfile(output_swf) :
			if os.path.isfile(output_swf+".out") :
				print("rm", output_swf+".out")
				exit(0)
			new_state = "WAIT"
		else:
			if os.path.isfile(output_swf+".out") :
				for line in open(output_swf+".out"):
					if "Traceback" in line:
						new_state = "ERROR"
						break
					if "Exception" in line:
						new_state = "ERROR"
						break
					if "Elapsed Time" in line:
						new_state = "DONE"
						break
			else:
				new_state = "NOOUT"
				
		if expedb[1] != new_state:
			print expedb[1], "!=", new_state, "for", expedb[0]
			if reset:
				if expedb[1] == "DOING":
					c.execute('UPDATE expes SET state="WAIT" WHERE hash=?', (expedb[0],))
				if expedb[1] == "DONE" and new_state == "WAIT":
					c.execute('UPDATE expes SET state="WAIT" WHERE hash=?', (expedb[0],))
			if new_state == "UNKNOWN":
				print "investigate '"+output_swf+"'"
	
	conn.commit()


def action_sql(cmd):
	c = conn.cursor()
	expes = c.execute(cmd).fetchall()
	for expedb in expes:
		print expedb
	conn.commit()


def usage():
	print("""
		run_valexpe_server.py get "houle"
			    <doer>
		
		run_valexpe_server.py done "hash"
		
		run_valexpe_server.py error "hash"
		
		run_valexpe_server.py print
		
		run_valexpe_server.py check_and_copy
			cat *.swf | wc -l == ...
		
		run_valexpe_server.py init_db
		
		run_valexpe_server.py init_db_dir
		
		run_valexpe_server.py init_db_dumb
		
		run_valexpe_server.py stats
		
		run_valexpe_server.py stats_db
		
		run_valexpe_server.py copy
		
		run_valexpe_server.py check_db (reset)
		
		run_valexpe_server.py SQL "SQL statement"
		
	""")
	exit(0)

if len(sys.argv) < 2:
	usage()

action = sys.argv[1]

if action == "get":
	if len(sys.argv) != 3:
		usage()
	action_get(sys.argv[2])
elif action == "done":
	if len(sys.argv) != 3:
		usage()
	action_done(sys.argv[2])
elif action == "error":
	if len(sys.argv) != 3:
		usage()
	action_error(sys.argv[2])
elif action == "print":
	if len(sys.argv) == 2:
		action_print()
	elif len(sys.argv) == 3:
		action_print(sys.argv[2])
	else:
		usage()
elif action == "check_and_copy":
	print("TODO")
elif action == "init_db":
	db_init_new_db()
elif action == "init_db_dir":
	db_init_new_db_dir()
elif action == "init_db_dumb":
	db_init_new_db_dumb()
elif action == "stats":
	action_stats()
elif action == "stats_db":
	action_stats_db()
elif action == "copy":
	action_copy()
elif action == "check_db":
	if len(sys.argv) == 2:
		action_check_db()
	elif len(sys.argv) == 3:
		action_check_db(True)
	else:
		usage()
elif action == "SQL":
	if len(sys.argv) == 3:
		action_sql(sys.argv[2])
	else:
		usage()
else:
	print("not an  action")
	usage()





# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
