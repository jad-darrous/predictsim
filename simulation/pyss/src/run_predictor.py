#!/usr/bin/python
# encoding: utf-8
'''
Runtime predictor tester.

Usage:
    predictor_tester.py <filename> <output_folder> tsafrir [-i] [-v]
    predictor_tester.py <filename> <output_folder> sgd <loss> <penalty> <max_cores> [-i] [-v]
    predictor_tester.py <filename>  <output_folder> passive-aggressive <loss> <max_cores> [-i] [-v]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode after script.
    tool                                           the machine learning technique to use. available: sgd,passive-aggressive,tsafrir.
    encoding                                       how to encode discret attributes (s.t. user ID). available: continuous, onehot.
    loss                                           for sgd: in  'squared_loss', 'huber', 'epsilon_insensitive', 'squared_epsilon_insensitive', 'maeloss'.
                                                   for passive-aggressive: in 'epsilon_insensitive', 'squared_epsilon_insensitive'
    penalty                                        in 'l2' , 'l1' , 'elasticnet'

'''
from docopt import docopt
arguments = docopt(__doc__, version='1.0.0rc2')

from base.prototype import _job_inputs_to_jobs
from base.workload_parser import parse_lines

if arguments['--verbose']==True:
    print(arguments)
    import warnings

if arguments['<max_cores>']==auto:
    with input_file as open(arguments['<filename>']):
        for line in input_file:
                if(line.lstrip().startswith(';')):
                        if(line.lstrip().startswith('; MaxProcs:')):
                                numproc = int(line.strip()[11:])
                                break
                        else:
                                continue
                else:
                        break
        if options.num_processors is None:
                parser.error("missing num processors")
elif eval(arguments['<max_cores>']):
    numproc=

with f as  open(arguments['<filename>'], 'rt'):
    jobs = _job_inputs_to_jobs(parse_lines(input_file), options.num_processors),


if arguments["tsafrir"]:


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
        print("sgd")

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
        #print(j)
        #print(Xf[i][4])
        #print(Xf_tsafir_mean3[i])
        #for k in range(0,len(np.array([j]))):
                #if np.array([j])[k] <-1 or np.array([j])[k]>1:
                    #print("k %s vector %s"%(k,np.array([j])))

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
