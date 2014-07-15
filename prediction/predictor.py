#!/usr/bin/python
# encoding: utf-8
'''
Runtime predictor.

Usage:
    meanpredict.py <filename> <extracted_data> <output_folder> randomforest <encoding> [-i] [-v]
    meanpredict.py <filename> <extracted_data> <output_folder> tsafrir [-i] [-v]
    meanpredict.py <filename> <extracted_data> <output_folder> svr <encoding> [-i] [-v]
    meanpredict.py <filename> <extracted_data> <output_folder> sgd <loss> <penalty> <encoding> <max_runtime> <max_cores> [-i] [-v]
    meanpredict.py <filename> <extracted_data> <output_folder> passive-aggressive <loss> <encoding> <max_runtime> <max_cores> [-i] [-v]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode after script.
    tool                                           the machine learning technique to use. available: svm, random_forest,sgd(incremental learning on whole log),passive-aggressive(incremental learning on whole log).
    encoding                                       how to encode discret attributes (s.t. user ID). available: continuous, onehot.
    loss                                           for sgd: in  'squared_loss', 'huber', 'epsilon_insensitive', 'squared_epsilon_insensitive', 'maeloss'.
                                                   for passive-aggressive: in 'epsilon_insensitive', 'squared_epsilon_insensitive'
    penalty                                        in 'l2' , 'l1' , 'elasticnet'

    Please format the csv file correctly before using: remove comments.

    Fields of swf file should be:

    job_id submit_time wait_time run_time proc_alloc cpu_time_used mem_used proc_req time_req mem_req status user_id group_id exec_id queue_id partition_id previous_job_id think_time

    Fields of extracted data (csv whitespace separated) should be:

    job_id user_id last_runtime last_runtime2 last_status last_status2 thinktime running_maxlength running_sumlength amount_running running_average_runtime running_allocatedcores
'''
from docopt import docopt
arguments = docopt(__doc__, version='1.0.0rc2')

__author__ = 'Valentin Reis  <valentin.reis@gmail.com>'
__version__ = '0.10'
__website__ = 'https://github.com/freuk/internship'
__license__ = 'WTFPL2.0'

#____ARGUMENT_MANAGEMENT____
if arguments['--verbose']==True:
    print(arguments)

if arguments["sgd"]:
    tool="sgd"
elif arguments["tsafrir"]:
    tool="tsafrir"
elif arguments["randomforest"]:
    tool="randomforest"
elif arguments["svr"]:
    tool="svr"
elif arguments["passive-aggressive"]:
    tool="passive-aggressive"
else:
    print "please use a valid tool."
    raise ValueError("tool")

if arguments["<encoding>"]:
    encoding=arguments["<encoding>"]
else:
    encoding=None

output_folder=arguments["<output_folder>"]


#____IMPORTS____
import numpy as np
from swfpy import io
import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import SGDRegressor
from sklearn.linear_model import PassiveAggressiveRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
from sklearn import preprocessing

from numpy.lib.recfunctions import append_fields
from numpy.lib.recfunctions import drop_fields
from numpy.lib.recfunctions import merge_arrays
from np_printutils import array_to_file
from np_printutils import np_array_to_file

#____FILE I/O____
print("opening the swf csv file")
swf_dtype=np.dtype([('job_id',np.int_), ('submit_time',np.float32) ,('wait_time',np.float32) ,('run_time',np.float32) ,('proc_alloc',np.int_) ,('cpu_time_used',np.float32) ,('mem_used',np.float32) ,('proc_req',np.int_) ,('time_req',np.float32) ,('mem_req',np.float32) ,('status',np.int_) ,('user_id',np.int_) ,('group_id',np.int_) ,('exec_id',np.int_) ,('queue_id',np.int_) ,('partition_id',np.int_) ,('previous_job_id',np.int_) ,('think_time',np.float32)])
with open (arguments["<filename>"], "r") as f:
    data=np.loadtxt(f, dtype=swf_dtype,comments=";")

print("opening the extracted data csv file")
extracted_data_dtype=np.dtype([('job_id',np.int_),('user_id',np.int_),('last_runtime',np.int_),('last_runtime2',np.float32),('last_status',np.int_),('last_status2',np.int_),('thinktime',np.float32),('running_maxlength',np.float32),('running_sumlength',np.float32),('amount_running',np.int_),('running_average_runtime',np.float32),('running_allocatedcores',np.int_),('t_since_last_sub',np.float32),('running_totalcores',np.int_),('last_runtime3',np.float32),('last_runtime4',np.float32),('usermean',np.float32)])
with open (arguments["<extracted_data>"], "r") as f:
    extracted_data=np.loadtxt(f, dtype=extracted_data_dtype)

#____DATA MANIPULATION____
#day of month
print("vectorizing functions for added info")
hod=np.vectorize(lambda x:datetime.datetime.fromtimestamp(int(x)).strftime('%H'))
dom=np.vectorize(lambda x:datetime.datetime.fromtimestamp(int(x)).strftime('%d'))
#day of week
dow=np.vectorize(lambda x:datetime.datetime.fromtimestamp(int(x)).weekday())

def mean2last(a,b,reqtime):
    if a==-1 or b==-1:
        return reqtime
    else:
        return (a+b)/2
def mean3last(a,b,c,reqtime):
    if a==-1 or b==-1 or c==-1:
        return reqtime
    else:
        return (a+b+c)/3
def mean4last(a,b,c,d,reqtime):
    if a==-1 or b==-1 or c==-1 or d==-1:
        return reqtime
    else:
        return (a+b+c+d)/4
#tsafir mean2last
tsafir=np.vectorize(mean2last)
tsafir3=np.vectorize(mean3last)
tsafir4=np.vectorize(mean4last)

print("calculating added info: tsafir mean2-3-4, hour of day, day of week, day of month")
X=drop_fields(data,['job_id','wait_time','run_time','proc_alloc','cpu_time_used','mem_used','mem_req','status','exec_id','queue_id','partition_id','previous_job_id','think_time'])

tsaf=tsafir(extracted_data['last_runtime'],extracted_data['last_runtime2'],data['time_req'])
tsaf3=tsafir3(extracted_data['last_runtime'],extracted_data['last_runtime2'],extracted_data['last_runtime3'],data['time_req'])
tsaf4=tsafir4(extracted_data['last_runtime'],extracted_data['last_runtime2'],extracted_data['last_runtime3'],extracted_data['last_runtime4'],data['time_req'])

X=append_fields(X,['hour_of_day','day_of_week','day_of_month','tsafir_mean','tsafir_mean3','tsafir_mean4'],[hod(data['submit_time']),dow(data['submit_time']),dom(X['submit_time']),tsaf,tsaf3,tsaf4],dtypes=[np.int_,np.int_,np.int_,np.float32,np.float32,np.float32])

#removing job id and user id, merging
#print(X.dtype)
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

    enc_user_id           = preprocessing.OneHotEncoder()
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
    #print("the format of X before going to np.array is:")
    #print(X.dtype)
    #print("the values are:")
    #print(X)

    Xf_proc_req                = np.reshape(X['proc_req'].astype('<f4'),(-1,1))
    Xf_time_req                = np.reshape(X['time_req'].astype('<f4'),(-1,1))
    Xf_tsafir_mean             = np.reshape(X['tsafir_mean'].astype('<f4'),(-1,1))
    Xf_tsafir_mean3            = np.reshape(X['tsafir_mean3'].astype('<f4'),(-1,1))
    Xf_tsafir_mean4            = np.reshape(X['tsafir_mean4'].astype('<f4'),(-1,1))
    Xf_hour_of_day                     = np.reshape(X['hour_of_day'].astype('<f4'),(-1,1))

    Xf_last_runtime            = np.reshape(X['last_runtime'].astype('<f4'),(-1,1))
    Xf_last_runtime2           = np.reshape(X['last_runtime2'].astype('<f4'),(-1,1))
    Xf_thinktime               = np.reshape(X['thinktime'].astype('<f4'),(-1,1))
    Xf_running_maxlength       = np.reshape(X['running_maxlength'].astype('<f4'),(-1,1))
    Xf_running_sumlength       = np.reshape(X['running_sumlength'].astype('<f4'),(-1,1))
    Xf_amount_running          = np.reshape(X['amount_running'].astype('<f4'),(-1,1))
    Xf_running_average_runtime = np.reshape(X['running_average_runtime'].astype('<f4'),(-1,1))
    Xf_running_allocatedcores  = np.reshape(X['running_allocatedcores'].astype('<f4'),(-1,1))
    Xf_t_since_last_sub        = np.reshape(X['t_since_last_sub'].astype('<f4'),(-1,1))
    #print("DEBUG")
    #print(max(X['running_totalcores']))
    Xf_running_totalcores      = np.reshape(X['running_totalcores'].astype('<f4'),(-1,1))
    Xf_last_runtime3           = np.reshape(X['last_runtime3'].astype('<f4'),(-1,1))
    Xf_last_runtime4           = np.reshape(X['last_runtime4'].astype('<f4'),(-1,1))
    Xf_usermean                = np.reshape(X['usermean'].astype('<f4'),(-1,1))

    if tool in ["sgd","passive-aggressive"]:
        #Scale the values to  [0,1]
        max_runtime                = float(arguments["<max_runtime>"])
        max_cores                  = float(arguments["<max_cores>"])
        Xf_proc_req                = Xf_proc_req/max_cores
        Xf_time_req                = Xf_proc_req/max_runtime
        Xf_tsafir_mean             = Xf_tsafir_mean/max_runtime
        Xf_tsafir_mean3            = Xf_tsafir_mean3/max_runtime
        Xf_tsafir_mean4            = Xf_tsafir_mean4/max_runtime
        Xf_hour_of_day             = Xf_hour_of_day/24.0
        Xf_last_runtime            = Xf_last_runtime/max_runtime
        Xf_last_runtime2           = Xf_last_runtime2/max_runtime

        max_thinktime=60*60*24
        scale_thinktime            = np.vectorize(lambda x:min(x/max_thinktime,1))
        Xf_thinktime               = scale_thinktime(Xf_thinktime)

        scale_maxlength            = np.vectorize(lambda x:min(x/max_runtime,1))
        Xf_running_maxlength       = scale_maxlength(Xf_running_maxlength)

        max_sumlength=max_runtime*10
        scale_sumlength            = np.vectorize(lambda x:min(x/max_sumlength,1))
        Xf_running_sumlength       = scale_sumlength(Xf_running_sumlength)

        scale_amount_running            = np.vectorize(lambda x:min(x/max_cores,1))
        Xf_amount_running          = scale_amount_running(Xf_amount_running)

        Xf_running_average_runtime = Xf_running_average_runtime/max_runtime
        Xf_running_allocatedcores  = Xf_running_allocatedcores/max_cores
        Xf_t_since_last_sub        = scale_thinktime(Xf_t_since_last_sub)

        scale_totalcores           = np.vectorize(lambda x:min(x/max_cores,1))
        Xf_running_totalcores      = scale_totalcores(Xf_running_totalcores)
        Xf_last_runtime3           = Xf_last_runtime3/max_runtime
        Xf_last_runtime4           = Xf_last_runtime4/max_runtime
        Xf_usermean                = Xf_usermean/max_runtime


    Xf=np.hstack((Xf_proc_req, Xf_time_req, Xf_tsafir_mean,Xf_tsafir_mean3,Xf_tsafir_mean4,Xf_hour_of_day, Xf_last_runtime, Xf_last_runtime2, Xf_thinktime, Xf_running_maxlength, Xf_running_sumlength, Xf_amount_running, Xf_running_average_runtime, Xf_running_allocatedcores,Xf_t_since_last_sub,Xf_running_totalcores,Xf_last_runtime3,Xf_last_runtime4,Xf_usermean,onehot_features))

    #for i in range(0,len(Xf[0,:])):
        #print "row %s" %(i+1)
        #print np.mean(Xf[:,i])
        #print max(Xf[:,i])
else:
    Xf=X.view(np.float32).reshape(X.shape + (-1,))

#At this point we have: Xf, yf, tsafir
#___LEARNING___
if tool=="random_forest":
    #____OFFLINE RANDOM FORESTS____

    start=int(len(Xf)*.7)
    i=int(len(Xf)*.8)
    Xlearn=Xf[start:i:1,:]
    Xtest=Xf[i:len(Xf),:]
    ylearn=yf[start:i:1]
    ytest=yf[i:len(yf)]
    tsafirtest=tsafir[i:len(yf)]
    forest=RandomForestRegressor(n_estimators=40, criterion='mse', max_depth=None, min_samples_split=2, min_samples_leaf=1, max_features='auto', bootstrap=True, oob_score=False, n_jobs=3, random_state=None, verbose=0, min_density=None, compute_importances=None)
    print("learning random forests")
    forest.fit(Xlearn,ylearn)
    print("prediction")
    pred=forest.predict(Xtest)
    np_array_to_file(pred,arguments["<output_folder>"]+"/prediction_rf")
elif tool=="tsafrir":
    #___TSAFRIR MEAN___

    def bound_req(pred,req):
        if pred<req:
            return pred
        else:
            return req
    bound_with_reqtime=np.vectorize(bound_req)
    np_array_to_file(bound_with_reqtime(tsafir,data['time_req']),arguments["<output_folder>"]+"/prediction_tsafrir")
elif tool=="svr":
    #___OFFLINE SVR___

    print("creating SVR")
    svr=SVR(kernel='linear', degree=3, gamma=0.0, coef0=0.0, tol=0.001, C=1.0, epsilon=0.1, shrinking=True, probability=False, cache_size=200, verbose=False, max_iter=-1, random_state=None)
    svr.fit(Xlearn,ylearn)
    pred=svr.predict(Xtest)
    np_array_to_file(pred,arguments["<output_folder>"]+"/prediction_rf")
elif tool in ["sgd","passive-aggressive"]:
    #___ONLINE LEARNING___

    from simpy import Environment,simulate,Monitor
    from swfpy import io
    if arguments['--verbose']==True:
        import logging
    from simpy.util import start_delayed

    if arguments['--verbose']==True:
        global_logger = logging.getLogger('global')
        hdlr = logging.FileHandler('predictor.log')
        formatter = logging.Formatter('%(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        global_logger.addHandler(hdlr)
    #Getting a simulation environment
    env = Environment()
    #logging function
    if arguments['--verbose']==True:
        def global_log(msg):
            prefix='%.1f'%env.now
            global_logger.info(prefix+': '+msg)
    else:
        def global_log(msg):
            pass

    if tool=="sgd":
        #___SGD___

        loss=arguments["<loss>"]
        if loss not in [ 'squared_loss', 'huber', 'epsilon_insensitive', 'squared_epsilon_insensitive','maeloss']:
            raise ValueError("invalid loss function")

        penalty=arguments["<penalty>"]
        if penalty not in ['l2' , 'l1' , 'elasticnet']:
            raise ValueError("invalid penalty function")

        model=SGDRegressor(loss=loss, penalty=penalty, alpha=0.0001, l1_ratio=0.15, fit_intercept=True, n_iter=5, shuffle=False, verbose=0, epsilon=0.1, random_state=None, learning_rate='invscaling', eta0=0.01, power_t=0.25, warm_start=False)
    if tool=="passive-aggressive":
        #___PASSIVE_AGGRESSIVE___

        loss=arguments["<loss>"]
        if loss not in [ 'epsilon_insensitive', 'squared_epsilon_insensitive']:
            raise ValueError("invalid loss function")
        model=PassiveAggressiveRegressor(C=1.0, fit_intercept=True, n_iter=5, shuffle=False, verbose=0, loss=loss, epsilon=0.1, random_state=None, class_weight=None, warm_start=False)

    pred=[]
    flag_bootstrapped=False
    def job_process(i):
        global flag_bootstrapped
        j=Xf[i]
        wait_time=data['wait_time'][i]
        run_time=data['run_time'][i]
        submit_time=data['submit_time'][i]

        yield env.timeout(submit_time)
        if flag_bootstrapped:
            #print("predicting")
            pred.append(min(abs(model.predict(j)),max_runtime,data['time_req'][i]))
        else:
            pred.append(0)

        yield env.timeout(wait_time+run_time)
        #print('4: time is %s,i= %s' % (env.now, i))
        model.partial_fit(np.array([j]),np.array([yf[i]]))
        #print('5: time is %s,i= %s' % (env.now, i))

        if not flag_bootstrapped:
            flag_bootstrapped=True
        if i % 1000==0:
            print "processed %s jobs so far" %i

    i=0
    for i in range(len(X)):
        env.start(job_process(i))
        i=i+1

    simulate(env)

    if arguments['--interactive']==True:
        print(arguments)
        from IPython import embed
        embed()

    if tool=="sgd":
        array_to_file(pred,arguments["<output_folder>"]+"/prediction_%s_%s_%s" %(tool,loss,penalty))
    elif tool=="passive-aggressive":
        array_to_file(pred,arguments["<output_folder>"]+"/prediction_%s_%s" %(tool,loss))

#interactive?
if arguments['--interactive']==True:
    print(arguments)
    from IPython import embed
    embed()
