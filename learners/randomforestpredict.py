#!/usr/bin/env python
# encoding: utf-8
'''
#!/usr/bin/python
random forest predictor.
DWTFPL v2.0

Usage:
    meanpredict.py <filename> <extracted_data> [-i] [-v]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode after script.

    Please format the csv file correctly before using: remove comments.

    Fields of swf file should be:

    job_id submit_time wait_time run_time proc_alloc cpu_time_used mem_used proc_req time_req mem_req status user_id group_id exec_id queue_id partition_id previous_job_id think_time

    Fields of extracted data (csv whitespace separated) should be:

    job_id user_id last_runtime last_runtime2 last_status last_status2 thinktime running_maxlength running_sumlength amount_running running_average_runtime running_allocatedcores
'''
from docopt import docopt
#retrieving arguments
arguments = docopt(__doc__, version='1.0.0rc2')

#verbose?
if '--verbose' in arguments.keys():
    print(arguments)

import numpy as np
from swfpy import io
import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

data=io.swfopen(arguments["<filename>"],output="np.array")

with open (arguments["<extracted_data>"], "r") as f:
    extracted_data=np.loadtxt(f, dtype={'names': ('job_id','user_id','last_runtime','last_runtime2','last_status','last_status2','thinktime','running_maxlength','running_sumlength','amount_running','running_average_runtime','running_allocatedcores'),'formats':(np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32)})
    #extracted_data=np.loadtxt(f)
#extracted_data.dtype={'names': ('job_id','user_id','last_runtime','last_runtime2','last_status','last_status2','thinktime','running_maxlength','running_sumlength','amount_running','running_average_runtime','running_allocatedcores'),'formats':(np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32)}

print(extracted_data)

#convert recarray to array
data=data.view(np.int32).reshape(data.shape + (-1,))
extracted_data=extracted_data.view(np.int32).reshape(extracted_data.shape + (-1,))

#data: 0-'job_id',1'submit_time',2-'wait_time',3-'run_time',4-'proc_alloc',5-'cpu_time_used',6-'mem_used',7'proc_req',8'time_req',9-'mem_req',10-'status',11'user_id',12'group_id',13-'exec_id',14-'queue_id',15-'partition_id',16-'previous_job_id',17-'think_time'.
#extracted_data: 0job_id 1user_id 2last_runtime 3last_runtime2 4last_status 5last_status2 6thinktime 7running_maxlength 8running_sumlength 9amount_running 10running_average_runtime 11running_allocatedcores

X=np.delete(data,[0,2,3,4,5,6,9,10,13,14,15,16,17],1)
#X: 0'submit_time',1'proc_req',2'time_req',3'user_id',4'group_id',

#X objective: 0'time_of_day',1'proc_req',2'time_req',3'user_id',4'group_id',5'think_time',6'mean_2last',7'mean_3last',8'value_last',9'value_2last',10'status_n-1',11'status_n-2',12'day_of_week',13'day_of_month'
X = np.hstack((X, np.zeros((X.shape[0], 5), dtype=X.dtype)))
#we have empty columns

dom=np.vectorize(lambda x:datetime.datetime.fromtimestamp(int(x)).strftime('%d'))
X[:,9]=dom(X[:,0])
#we have day_of_month in 13
dow=np.vectorize(lambda x:datetime.datetime.fromtimestamp(int(x)).weekday())
X[:,8]=dow(X[:,0])
#we have day_of_week in 12
s=3600*24
X[:,0]=X[:,0] %s
#we have time_of_day in 0

#more on extracted features:
#-calculating tsafir mean:
X_extract=extracted_data
def mean2last(a,b,reqtime):
    if a==-1 or b==-1:
        return reqtime
    else:
        return (a+b)/2

X[:,5]=np.vectorize(mean2last)(X_extract[:,2],X_extract[:,3],X[:,2]) #vector sum

#removing job id and user id
X_extract=np.delete(X_extract,[0,1],1)
#joining the extracted data:
X=np.concatenate((X, X_extract), axis=1)

np.savetxt("foo.csv", X, delimiter=" ",fmt='%.2e',)

#final values:
#0'time_of_day',1'proc_req',2'time_req',3'user_id',4'group_id',5'mean_2last',6'day_of_week',7'day_of_month',8'last_runtime',9'last_runtime2',10'last_status',11'last_status2',12'thinktime',13'running_maxlength',14'running_sumlength',15'amount_running',16'running_average_runtime',17'running_allocatedcores,18'tsafir'
#objective
y=data[:,3]

i=int(len(X)*.8)
Xlearn=X[1:i:1,:]
Xtest=X[i:len(X),:]
ylearn=y[1:i:1]
ytest=y[i:len(y)]

#big int least squares


#TSAFIR BASELINE
print(ytest.shape)
print(Xtest[:,18].shape)
err=Xtest[:,18]-ytest
print(err.shape)

tsafir_squares=np.mean(err**2)

#svm random_forest
tool="svm"

#RANDOM FOREST
if tool=="random_forest":
    print("creating rand forests regressor")
    forest=RandomForestRegressor(n_estimators=100, criterion='mse', max_depth=None, min_samples_split=2, min_samples_leaf=1, max_features='auto', bootstrap=True, oob_score=False, n_jobs=3, random_state=None, verbose=0, min_density=None, compute_importances=None)
    print("learning random forests")
    forest.fit(Xlearn,ylearn)

    print("Prediction!")
    err=forest.predict(Xtest)-ytest
    forest_squares=np.mean(err**2)
elif tool=="svm":




#interactive?
if '--interactive' in arguments.keys():
    from IPython import embed
    embed()
