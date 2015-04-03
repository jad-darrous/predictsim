#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import sys
import sqlite3
import hashlib
import os
import time
import glob

expe_name = "SDSC-BLUE"
num_processors = 1152
expe_dir = "../../../experiments/data/"+expe_name
conn = sqlite3.connect(expe_dir+"/run.db", timeout=120)
ouput_dir = expe_dir+"/simulations/"
input_file = expe_dir+"/swf/log.swf"

#dict_path = '../../../experiments/experiment_dicts.py'
dict_path = '../../../experiments/experiment_dicts_kth.py'


def nice(s):
	# transform an dict into something command-line compatible, the ugliest way!
	print "DO NOT USE nice()!"
	return str(s).translate(None, " ':/(){},\"").replace("name", "").replace("predictor_sgdlinear", "gdl").replace("max_coresauto", "").replace("regularizationl2", "").replace("lambda4000000000", "").replace("gdNAG", "")



def hash(s):
	print "DO NOT USE hash()!"
	return hashlib.sha1(nice(s)).hexdigest()



def sched2filename(s):
	p = s["predictor"]
	if p != None:
		if p["name"] == "predictor_sgdlinear":
			res = p["name"].replace("_", "")+"I"
			res += p["rightside"]+"I"
			res += str(p["rightparam"])+"I"
			res += p["leftside"]+"I"
			res += str(p["leftparam"])+"I"
			res += str(p["threshold"])+"I"
			res += p["weight"].translate(None, " ':/(){},\"+*")
		else:
			res = p["name"].replace("_", "")
	else:
		res = "None"

	if s["corrector"] != None:
		cor = s["corrector"]["name"]
	else:
		cor = "None"
	return "res_"+s["name"]+"_"+res+"_"+cor+".swf.gz"

def opt2filename(opt):
	return sched2filename(opt["scheduler"])

def opt2hash(opt):
	return hashlib.sha1(
		str(opt["input_file"])+
		str(opt["num_processors"])+
		opt2filename(opt)).hexdigest()

def filename2opt(s):
	s = s.split("/")[-1]
	s = s.rstrip(".out")
	s = s.rstrip(".gz")
	s = s.rstrip(".swf")

	ss = s.split("_")
	
	#no predictor nor corrector
	if ss[-1] == 'None' and ss[-2] == 'None':
		corrector = None
		predictor = None
		sched = '_'.join(ss[1:-2])
	else:
		tttt = [len(x) for x in ss]
		opt_index = tttt.index(max(tttt))

		corrector = "_".join(ss[opt_index+1:len(ss)])
		sched = "_".join(ss[1:opt_index])
		o = ss[opt_index]
		oo = o.split("I")
		if oo[0] != "predictorsgdlinear":
			raise "only predictorsgdlinear is supported"
		
		p = {"name":"predictor_sgdlinear",
		"max_cores":"auto",
		"eta":5000,
		"loss":"composite",
		"quadratic":True,
		"cubic": False,
		"gd": "NAG",
		"regularization":"l2",
		"lambda":4000000000}
		
		p["rightside"] = oo[1]
		p["rightparam"] = float(oo[2])
		if p["rightparam"] >= 1:
			p["rightparam"] = int(p["rightparam"])
		p["leftside"] = oo[3]
		p["leftparam"] = float(oo[4])
		if p["leftparam"] >= 1:
			p["leftparam"] = int(p["leftparam"])
		p["threshold"] = int(oo[5])

		weightnice={"1":"1",
			"5logrm":"5+log(r/m)",
			"5logmr":"5+log(m/r)",
			"11log1rm":"11+log(1/(r*m))",
			"1logmr":"1+log(m*r)"
			}
		p["weight"] = weightnice[oo[6]]
		
		predictor = p
	
	opt = {'output_swf': 'TBD',
		'num_processors': num_processors,
		'input_file': input_file,
		'stats': False,
		'scheduler': {
			'corrector': {'name': corrector},
			'progressbar': False,
			'name': sched,
			'predictor': predictor}}
	
	opt["output_swf"] = ouput_dir+opt2filename(opt)
	
	return opt




def db_init_new_db():
	
	exec(open(dict_path).read())
	configs=[
		{
		'input_file': input_file,
		"num_processors":num_processors,
		'output_swf': ouput_dir+sched2filename(s),
		'stats': False,
		"scheduler":s
		}
		for s in sched_configs]
	
	
	c = conn.cursor()

	# Create table
	c.execute('''CREATE TABLE expes (hash text, state text, doer text, options text)''')

	# Insert a row of data
	for conf in configs:
		c.execute("INSERT INTO expes VALUES (?, 'WAIT', 'None', ?)", (opt2hash(conf), json.dumps(conf)))

	# Save (commit) the changes
	conn.commit()
	

def db_init_new_db_dir():
	
	curs = conn.cursor()

	# Create table
	curs.execute('''CREATE TABLE expes (hash text, state text, doer text, options text)''')
	
	
	exec(open(dict_path).read())
	nconf = len(sched_configs)
	nconf_skipped = 0
	nconf_finished = 0
	state = "WAIT"
	for s in sched_configs:
		output_swf = ouput_dir+sched2filename(s)
		state = "WAIT"
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
				state = "ERROR"
			else:
				nconf_finished += 1
				state = "DONE"
		conf = {
			'input_file': input_file,
			"num_processors":num_processors,
			'output_swf': output_swf,
			'stats': False,
			"scheduler":s
			}
		curs.execute("INSERT INTO expes VALUES (?, ?, 'None', ?)", (opt2hash(conf), state, json.dumps(conf)))
		
	print nconf, "expes =", len(sched_configs), "todo +", nconf_skipped, "in error +", nconf_finished, "finished"



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
	
	if expe != None:
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
		output_swf = ouput_dir+sched2filename(s)
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
		output_swf = ouput_dir+sched2filename(s)
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


def unnice(s):
	
	s = s.split("/")[-1]
	s = s.rstrip(".out")
	s = s.rstrip(".gz")
	s = s.rstrip(".swf")

	ss = s.split("_")
	tttt = [len(x) for x in ss]
	opt_index = tttt.index(max(tttt))

	sched = '_'.join(ss[1:opt_index])
	corrector = "_".join(ss[opt_index+1:len(ss)])
	o = ss[opt_index]

	ks = ['loss', 'weight', 'cubic', 'eta', 'threshold', 'rightside', 'rightparam', 'quadratic', 'leftside', 'leftparam']

	a = [(o.find(x), x) for x in ks]
	a.sort()
	t = o.lstrip(a[0][1])
	opt = {"name":"predictor_sgdlinear",
		"max_cores":"auto",
		"eta":5000,
		"loss":"composite",
		"quadratic":True,
		"cubic": False,
		"gd": "NAG",
		"regularization":"l2",
		"lambda":4000000000}

	for i in range(1, len(a)):
		tt = t.split(a[i][1])
		opt[a[i-1][1]] = tt[0].strip('gdl')
		t = a[i][1].join(tt[1:len(tt)])

	opt[a[len(a)-1][1]] = t.strip('gdl')

	weightnice={"1":"1",
		"5+logrm":"5+log(r/m)",
		"5+logmr":"5+log(m/r)",
		"11+log1r*m":"11+log(1/(r*m))",
		"1+logm*r":"1+log(m*r)"
		}
	if opt["weight"] != "":
		opt["weight"] = weightnice[opt["weight"]]
	
		opt["threshold"] = int(opt["threshold"])
		opt["leftparam"] = float(opt["leftparam"])
		if opt["leftparam"] >= 1:
			opt["leftparam"] = int(opt["leftparam"])
		opt["rightparam"] = float(opt["rightparam"])
		if opt["rightparam"] >= 1:
			opt["rightparam"] = int(opt["rightparam"])
		opt["eta"] = int(opt["eta"])

	finalopt = {'output_swf': 'res.swf',
		'num_processors': 80640,
		'input_file': '../../../experiments/data/CEA-curie_sample/swf/log.swf',
		'stats': False,
		'scheduler': {'corrector': {'name': corrector},
			'progressbar': False,
			'name': sched,
			'predictor': opt}}

	return finalopt


def ascii_encode(x):
	if isinstance(x, unicode):
		return x.encode('ascii')
	return x

def ascii_encode_dict(data):
    return dict(map(ascii_encode, pair) for pair in data.items())

def action_nice(opts):
	#print type(opts)
	opt = json.loads(opts, object_hook=ascii_encode_dict)
	s = opt["scheduler"]
	print ouput_dir+"res_"+s["name"]+"_"+nice(str(s["predictor"]).encode('ascii'))+"_"+nice(str(s["corrector"]).encode('ascii'))+".swf.gz"


def init_db_curie():
	#limit = 10
	res = {}
	ouput_dirSAVE = "../../../experiments/data/CEA-curie/simulations_SAVE/"
	for file in glob.glob(ouput_dirSAVE+"*.gz"):
		#print "#############################"
		#print(file)
		#print "---------------------------"
		try:
			opt = filename2opt(file)
		except:
			opt = unnice(file)
		#print opt
		#print "---------------------------"
		#print ouput_dir+opt2filename(opt)
		#print opt2hash(opt)
		fro=file
		too=ouput_dir+opt2filename(opt)
		#print fro
		#print too
		
		os.system("cp \""+fro+"\" \""+too+"\"")
		'''res[hash] = {
			"outfile":file,
			"swffile": xx,
			"oldformat": True,
			"hash":hash,
			"comptime": 12,
			"state":xx
			}'''
		
		
		
		#limit -= 1
		#if limit == 0:
			#break
	
	
	
	return

	
	
	









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
		
		run_valexpe_server.py init_db_curie
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
elif action == "init_db_curie":
	init_db_curie()
else:
	print("not an  action")
	usage()





# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
