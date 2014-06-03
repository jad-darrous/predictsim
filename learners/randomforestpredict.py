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
import datetime

data=io.swfopen(arguments["<filename>"],output="np.array")
#print data

data=data.view(np.int32).reshape(data.shape + (-1,))

y=data[:,3]
statuses=data[:,10]

#data: 0-'job_id',1'submit_time',2-'wait_time',3-'run_time',4-'proc_alloc',5-'cpu_time_used',6-'mem_used',7'proc_req',8'time_req',9-'mem_req',10-'status',11'user_id',12'group_id',13-'exec_id',14-'queue_id',15-'partition_id',16-'previous_job_id',17-'think_time'.

X=np.delete(data,[0,2,3,4,5,6,9,10,13,14,15,16,17],1)
#X: 0'submit_time',1'proc_req',2'time_req',3'user_id',4'group_id',

#X objective: 0'time_of_day',1'proc_req',2'time_req',3'user_id',4'group_id',5'think_time',6'mean_2last',7'mean_3last',8'value_last',9'value_2last',10'status_n-1',11'status_n-2',12'day_of_week',13'day_of_month'
X = np.hstack((X, np.zeros((X.shape[0], 9), dtype=X.dtype)))
#we have empty columns

dom=np.vectorize(lambda x:datetime.datetime.fromtimestamp(int(x)).strftime('%d'))
X[:,13]=dom(X[:,0])
#we have day_of_month in 13
dow=np.vectorize(lambda x:datetime.datetime.fromtimestamp(int(x)).weekday())
X[:,12]=dow(X[:,0])
#we have day_of_week in 12
s=3600*24
X[:,0]=X[:,0] %s
#we have time_of_day in 0

#tsafir mean calculation
#along with: mean_3last, value_last , value_2last, status_n-1, status_n-2.
users=set(X[:,3])

#we do this: WITH CSIM.py
#pastruntime1={}
#pastsubtime={}
#pastruntime2={}
#pastruntime0={}
#paststatus1={}
#paststatus2={}
##add statuses.
#for uid in users:
    #pastsubtime[uid]=-1
    #pastruntime1[uid]=-1
    #pastruntime2[uid]=-1
    #pastruntime0[uid]=-1
    #paststatus1[uid]=-1
    #paststatus2[uid]=-1

#predictions=[]
#for i in range(X.shape[0]):
    #uid=X[i,3]
    #r1=pastruntime1[uid]
    #r2=pastruntime2[uid]
    #r0=pastruntime0[uid]

    ##past means_2 means_3
    #if not r1==-1 and not r2==-1:
      #pred2=(r1+r2)/2
      #X[i,6]=pred2
      #if not r0==-1:
        #pred3=(r1+r2+r0)/3
        #X[i,7]=pred2
      #else:
        #X[i,7]=X[i,2]
    #else:
      #X[i,6]=X[i,2]
      #X[i,7]=X[i,2]
    #pastruntime0[uid]=pastruntime1[uid]
    #pastruntime1[uid]=pastruntime2[uid]
    #pastruntime2[uid]=y[i]

    ##past status
    #s1=paststatus1[uid]
    #s2=paststatus2[uid]
    #X[i,10]=s1
    #X[i,11]=s2
    #paststatus2[uid]=s1
    #paststatus1[uid]=statuses[i]

    ##past runtimes
    #def test(x,i):
        #if x<0:
            #return y[i]
        #else:
            #return x
    #X[i,10]=test(pastruntime1[uid],i)
    #X[i,11]=test(pastruntime2[uid],i)

    ##Thinktime
    #if pastsubtime[uid]>0:
        #X[i,5]=data[i,0]-pastsubtime[uid]-pastruntime2[uid]




i=int(len(X)*.8)
Xlearn=X[1:i:1,:]
Xtest=X[i:len(X),:]


#interactive?
if '--interactive' in arguments.keys():
    from IPython import embed
    embed()
