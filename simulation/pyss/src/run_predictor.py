#!/usr/bin/pypy
# encoding: utf-8
'''
Runtime predictor tester.

Usage:
    run_predictor.py <swf_file> <config_file> <output_file> <measurement_file> <coeff_file> [-i] [-v]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode at key points in script.
'''

from base.docopt import docopt
from base.prototype import _job_input_to_job
from base.workload_parser import parse_lines
#from base.np_printutils import array_to_file
#from base.np_printutils import array_to_file_n
#from base.np_printutils import np_array_to_file
from simpy import Environment,simulate,Monitor
from simpy.util import start_delayed

#parameters for the argument retrieval:
supported_losses=['squared_loss']
supported_penalties=['none']

#Retrieve arguments
arguments = docopt(__doc__, version='1.0.0rc2')

#Manage Verbosity
if arguments['--verbose']==True:
    print("You asked for verbose output. File \"predictor.log\" will be created in this directory.")
    print(arguments)
    import warnings
    import logging
    global_logger = logging.getLogger('global')
    hdlr = logging.FileHandler('predictor.log')
    formatter = logging.Formatter('%(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    global_logger.addHandler(hdlr)
    def global_log(msg):
        prefix='%.1f'%env.now
        global_logger.info(prefix+': '+msg)
else:
    def global_log(msg):
        pass

#argement management: max_cores
config = {}
execfile(arguments["<config_file>"], config)
if config['scheduler']['predictor']['max_cores']=="auto":
    with open(arguments['<swf_file>']) as input_file:
        num_processors=None
        for line in input_file:
            if(line.lstrip().startswith(';')):
                if(line.lstrip().startswith('; MaxProcs:')):
                    num_processors = int(line.strip()[11:])
                    break
                else:
                    continue
            else:
                break
        if num_processors is None:
            raise ValueError("Missing MaxProcs in header or cli argument.")
elif config['max_cores'].isdigit():
    num_processors=eval(config['max_cores'])
else:
    raise ValueError("max_cores must be an integer or \"auto\"")

def iprint(p=None):
    """interactive print: switch to interactive python shell if --interactive is asked."""
    if not p==None:
        print(p)
    if arguments['--interactive']==True:
        from IPython import embed
        embed()

def _my_job_inputs_to_jobs(job_inputs, total_num_processors):
    for job_input in job_inputs:
        j=_job_input_to_job(job_input, total_num_processors)
        j.wait_time=job_input.wait_time
        yield j

iprint("Opening the swf file.")
with open(arguments['<swf_file>'], 'rt') as  f:
    jobs = _my_job_inputs_to_jobs(parse_lines(f), num_processors)
    print("Parsed swf file.")

    print("Choosing predictor.")
    if config["scheduler"]["predictor"]["name"]=="predictor_tsafrir":
        from predictors.predictor_tsafrir import PredictorTsafrir
        predictor=PredictorTsafrir({})
    elif config["scheduler"]["predictor"]["name"]=="predictor_clairvoyant":
        from predictors.predictor_clairvoyant import PredictorClairvoyant
        predictor=PredictorClairvoyant({})
    elif config["scheduler"]["predictor"]["name"]=="predictor_reqtime":
        from predictors.predictor_reqtime import PredictorReqtime
        predictor=PredictorReqtime({})
    elif config["scheduler"]["predictor"]["name"]=="predictor_double_reqtime":
        from predictors.predictor_double_reqtime import PredictorDoubleReqtime
        predictor=PredictorDoubleReqtime({})
    elif config["scheduler"]["predictor"]["name"]=="predictor_sgdlinear":
        #if arguments["<loss>"] not in ["squared_loss"]:
            #raise ValueError("loss not supported. supported losses=%s"%(supported_losses.__str__()))
        #if arguments["<penalty>"] not in ["none"]:
            #raise ValueError("penalty not supported. supported penalties=%s"%(supported_penalties.__str__()))
        from predictors.predictor_sgdlinear import PredictorSgdlinear
        predictor=PredictorSgdlinear(config)
    elif config["scheduler"]["predictor"]["name"]=="predictor_knn":
        from predictors.predictor_knn import PredictorKNN
        predictor=PredictorKNN(config)
    else:
        raise ValueError("no valid predictor specified")
    iprint("Predictor created.")

    #Getting a simulation environment
    env = Environment()

    pred=[]
    loss=[]
    if hasattr(predictor,"model"):
        coeffs=[]

    #system variables
    running_jobs=[]

    def job_process(j):
        yield env.timeout(j.submit_time)
        l=predictor.predict(j,env.now,running_jobs)
        if not l==None:
            loss.append(l)
        pred.append(j.predicted_run_time)
        yield env.timeout(j.wait_time)
        running_jobs.append(j)
        yield env.timeout(j.actual_run_time)
        running_jobs.remove(j)
        predictor.fit(j,env.now)
        #if hasattr(predictor,"model"):
            #coeffs.append(predictor.model.model.w)

    #Starting the replay
    for job in jobs:
        env.start(job_process(job))
    simulate(env)

    if arguments['--interactive']==True:
        print(arguments)
        from IPython import embed
        embed()

#print pred

def array_to_file(L,fn):
    with open(fn,"w") as f:
        for item in L:
            f.write("%s\n" % item)

array_to_file(pred,arguments["<output_file>"])
array_to_file(loss,arguments["<measurement_file>"])
#if hasattr(predictor,"model"):
    #print coeffs
    #np_array_to_file(coeffs,arguments["<coeff_file>"])
if hasattr(predictor,"model"):
    with open(arguments["<coeff_file>"],"w") as f:
        for item in coeffs:
          f.write("%s\n" % item)
