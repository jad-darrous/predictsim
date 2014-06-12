#!/usr/bin/env python
# encoding: utf-8
'''
#!/usr/bin/python
runtime predictor.
DWTFPL v2.0

Usage:
    meanpredict.py <filename> <extracted_data> <tool> <encoding> [-i] [-v]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode after script.
    tool                                           the machine learning technique to use. available: svm, random_forest
    encoding                                       how to encode discret attributes (s.t. user ID). available: continuous, onehot.

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
if arguments['--verbose']==True:
    print(arguments)

#svm random_forest
tool=arguments["<tool>"]
#normal onehot
encoding=arguments["<encoding>"]

import numpy as np
from swfpy import io
import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
from sklearn import preprocessing

from numpy.lib.recfunctions import append_fields
from numpy.lib.recfunctions import drop_fields
from numpy.lib.recfunctions import merge_arrays

print("opening the swf csv file")
swf_dtype=np.dtype([('job_id',np.int_), ('submit_time',np.float32) ,('wait_time',np.float32) ,('run_time',np.float32) ,('proc_alloc',np.int_) ,('cpu_time_used',np.float32) ,('mem_used',np.float32) ,('proc_req',np.int_) ,('time_req',np.float32) ,('mem_req',np.float32) ,('status',np.int_) ,('user_id',np.int_) ,('group_id',np.int_) ,('exec_id',np.int_) ,('queue_id',np.int_) ,('partition_id',np.int_) ,('previous_job_id',np.int_) ,('think_time',np.float32)])
with open (arguments["<filename>"], "r") as f:
    data=np.loadtxt(f, dtype=swf_dtype)

print("opening the extracted data csv file")
extracted_data_dtype=np.dtype([('job_id',np.int_),('user_id',np.int_),('last_runtime',np.int_),('last_runtime2',np.float32),('last_status',np.int_),('last_status2',np.int_),('thinktime',np.float32),('running_maxlength',np.float32),('running_sumlength',np.float32),('amount_running',np.int_),('running_average_runtime',np.float32),('running_allocatedcores',np.int_)])
with open (arguments["<extracted_data>"], "r") as f:
    extracted_data=np.loadtxt(f, dtype=extracted_data_dtype)


#______data field modification vectorized functions:
#day of month
print("vectorizing functions for added info")
dom=np.vectorize(lambda x:datetime.datetime.fromtimestamp(int(x)).strftime('%d'))
#day of week
dow=np.vectorize(lambda x:datetime.datetime.fromtimestamp(int(x)).weekday())
def mean2last(a,b,reqtime):
    if a==-1 or b==-1:
        return reqtime
    else:
        return (a+b)/2
#tsafir mean2last
tsafir=np.vectorize(mean2last)

print("calculating added info: tsafir mean, day of week, day of month")
X=drop_fields(data,['job_id','wait_time','run_time','proc_alloc','cpu_time_used','mem_used','mem_req','status','exec_id','queue_id','partition_id','previous_job_id','think_time'])
X=append_fields(X,['day_of_week','day_of_month','tsafir_mean'],[dow(data['submit_time']),dom(X['submit_time']),tsafir(extracted_data['last_runtime'],extracted_data['last_runtime2'],data['time_req'])],dtypes=[np.int_,np.int_,np.float32])

#removing job id and user id, merging
print(X.dtype)
print("merging all data into one")
X=merge_arrays((X,drop_fields(extracted_data,['job_id','user_id'])),usemask=False,asrecarray=True,flatten=True)
#X=merge_arrays((X,drop_fields(extracted_data,['job_id','user_id'])),asrecarray=True,flatten=True)

#__True runtime
yf=data['run_time'].astype('<f4')

#__tsafir runtime
tsafir=X['tsafir_mean']

if encoding=="onehot":
    print("encoding in onehot")
    mms = preprocessing.MinMaxScaler()
    enc_user_id = preprocessing.OneHotEncoder()

    X_onehot_user_id      = np.array( enc_user_id.fit_transform(np.reshape(X['user_id'],(-1,1))).toarray())
    enc_group_id          = preprocessing.OneHotEncoder()

    X_onehot_group_id     = np.array( enc_group_id.fit_transform(np.reshape(X['group_id'],(-1,1))).toarray())
    enc_day_of_week       = preprocessing.OneHotEncoder()

    X_onehot_day_of_week  = np.array( enc_day_of_week.fit_transform(np.reshape(X['day_of_week'],(-1,1))).toarray())
    enc_day_of_month      = preprocessing.OneHotEncoder()

    X_onehot_day_of_month = np.array( enc_day_of_month.fit_transform(np.reshape(X['day_of_month'],(-1,1))).toarray())
    enc_last_status       = preprocessing.OneHotEncoder()

    X_onehot_last_status  = np.array( enc_last_status.fit_transform(mms.fit_transform(np.reshape(X['last_status'],(-1,1)))).toarray())
    enc_last_status2      = preprocessing.OneHotEncoder()

    X_onehot_last_status2 = np.array( enc_last_status2.fit_transform(mms.fit_transform(np.reshape(X['last_status2'],(-1,1)))).toarray())
    onehot_features       = np.hstack((X_onehot_user_id,X_onehot_group_id,X_onehot_day_of_week,X_onehot_last_status,X_onehot_last_status2))

    X=drop_fields(X,['user_id','group_id','day_of_week','day_of_month','last_status','last_status2'])
    print("the format of X before going to np.array is:")
    print(X.dtype)
    print("the values are:")
    print(X)
    #Xf=X.view(np.float32).reshape(X.shape + (-1,))

    #dtype=[('submit_time', '<f4'), ('proc_req', '<i8'), ('time_req', '<f4'), ('tsafir_mean', '<f4'), ('last_runtime', '<i8'), ('last_runtime2', '<f4'), ('thinktime', '<f4'), ('running_maxlength', '<f4'), ('running_sumlength', '<f4'), ('amount_running', '<i8'), ('running_average_runtime', '<f4'), ('running_allocatedcores', '<i8')]

    Xf_proc_req                = np.reshape(X['proc_req'].astype('<f4'),(-1,1))
    Xf_time_req                = np.reshape(X['time_req'].astype('<f4'),(-1,1))
    Xf_tsafir_mean             = np.reshape(X['tsafir_mean'].astype('<f4'),(-1,1))
    Xf_last_runtime            = np.reshape(X['last_runtime'].astype('<f4'),(-1,1))
    Xf_last_runtime2           = np.reshape(X['last_runtime2'].astype('<f4'),(-1,1))
    Xf_thinktime               = np.reshape(X['thinktime'].astype('<f4'),(-1,1))
    Xf_running_maxlength       = np.reshape(X['running_maxlength'].astype('<f4'),(-1,1))
    Xf_running_sumlength       = np.reshape(X['running_sumlength'].astype('<f4'),(-1,1))
    Xf_amount_running          = np.reshape(X['amount_running'].astype('<f4'),(-1,1))
    Xf_running_average_runtime = np.reshape(X['running_average_runtime'].astype('<f4'),(-1,1))
    Xf_running_allocatedcores  = np.reshape(X['running_allocatedcores'].astype('<f4'),(-1,1))

    Xf=np.hstack((Xf_proc_req, Xf_time_req, Xf_tsafir_mean, Xf_last_runtime, Xf_last_runtime2, Xf_thinktime, Xf_running_maxlength, Xf_running_sumlength, Xf_amount_running, Xf_running_average_runtime, Xf_running_allocatedcores,onehot_features))
else:
    Xf=X.view(np.float32).reshape(X.shape + (-1,))



#dirty fix for nan values
#Xf=np.nan_to_num(X)
#yf=np.nan_to_num(y)

start=int(len(Xf)*.7)
i=int(len(Xf)*.8)
Xlearn=Xf[start:i:1,:]
Xtest=Xf[i:len(Xf),:]
ylearn=yf[start:i:1]
ytest=yf[i:len(yf)]
tsafirtest=tsafir[i:len(yf)]

#TSAFIR BASELINE
print("baseline mean: %s" %(np.mean(tsafirtest)))
print("calculating baseline squared error:")
tsafir_squares=np.mean((tsafirtest-ytest)**2)
print("tsafir_squares="+str(tsafir_squares))


#RANDOM FOREST
if tool=="random_forest":
    print("creating random forests regressor")
    forest=RandomForestRegressor(n_estimators=40, criterion='mse', max_depth=None, min_samples_split=2, min_samples_leaf=1, max_features='auto', bootstrap=True, oob_score=False, n_jobs=3, random_state=None, verbose=0, min_density=None, compute_importances=None)
    print("learning random forests")
    forest.fit(Xlearn,ylearn)
    print("Prediction!")
    pred=forest.predict(Xtest)
    print("prediction mean: %s" %(pred))
    err=pred-ytest
    forest_squares=np.mean(err**2)
    print("forest_squares: %s" %forest_squares)
elif tool=="svm":
    print("creating SVR")
    svr=SVR(kernel='linear', degree=3, gamma=0.0, coef0=0.0, tol=0.001, C=1.0, epsilon=0.1, shrinking=True, probability=False, cache_size=200, verbose=False, max_iter=-1, random_state=None)
    print("learning SVR")
    svr.fit(Xlearn,ylearn)
    print("Prediction!")
    svr_pred=svr.predict(Xtest)
    err=svr_pred-ytest
    svr_squares=np.mean(err**2)
    print(svr_squares)


pred=np.reshape(pred,(-1,1))
tsaf=np.reshape(tsafirtest,(-1,1))
ytest=np.reshape(ytest,(-1,1))
np.savetxt("prediction_randomforest_40_trees",np.hstack((pred,tsafir,ytest)))

#interactive?
if arguments['--interactive']==True:
    print(arguments)
    from IPython import embed
    embed()
