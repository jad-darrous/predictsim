import pandas as pd
import pandas.io.data
from pandas import Series, DataFrame
import sqlite3
import json
import numpy as np

import re
import os
import sys


if len(sys.argv) != 3:
	print "usage: pypy -OO fill_metrics.py <path_to_run.db> <input_metrics.csv>"
	exit(1)

path_to_db = sys.argv[1]
input_metrics = sys.argv[2]


df = pd.read_csv(input_metrics, sep=" ")
df["hash"] = None
df["simultime"] = None
df["scheduler"] = None
df["corrector"] = None
df["predictor"] = None
df["prightside"] = None
df["prightparam"] = None
df["pleftside"] = None
df["pleftparam"] = None
df["pthreshold"] = None
df["pweight"] = None
df.head()


conn = sqlite3.connect(path_to_db, timeout=120)
c = conn.cursor()
for i in range(len(df['name'])):
	input_swf = df['name'][i]

	expes = c.execute("SELECT * FROM expes WHERE options LIKE '%"+input_swf+"%'").fetchone()
    
	if os.path.isfile(input_swf+".out") :
		for line in open(input_swf+".out"):
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
				df["simultime"][i] = sec + minu*60 + hour*3600
				break
		
	if expes != None:
		df["hash"][i] = expes[0]
		params = json.loads(expes[3])

		df["scheduler"][i] = params['scheduler']['name']
		df["corrector"][i] = params['scheduler']['corrector']['name']
		df["predictor"][i] = params['scheduler']['predictor']['name']
		if "predictor_sgdlinear" ==  params['scheduler']['predictor']['name']:
			predictor = params['scheduler']['predictor']
			df["prightside"][i] = predictor['rightside']
			df["prightparam"][i] = predictor['rightparam']
			df["pleftside"][i] = predictor['leftside']
			df["pleftparam"][i] = predictor['leftparam']
			df["pthreshold"][i] = predictor['threshold']
			df["pweight"][i] = predictor['weight']
	else:
		#print "NOT FOUND:", input_swf
		pass

#conn.commit()
conn.close()

print df.to_csv(sep=" ",na_rep="NA")


