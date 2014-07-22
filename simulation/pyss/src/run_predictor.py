#!/usr/bin/python
# encoding: utf-8
'''
Runtime predictor tester.

Usage:
    run_predictor.py <filename> <output_folder> tsafrir [-i] [-v]
    run_predictor.py <filename> <output_folder> clairvoyant [-i] [-v]
    run_predictor.py <filename> <output_folder> sgd_linear <max_cores> <loss> <penalty> <eta> <alpha> <beta> [-i] [-v]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode at key points in script.
    loss                                           for sgd: for now, 'squared_loss'.
                                                   for passive-aggressive: in 'epsilon_insensitive', 'squared_epsilon_insensitive'
    penalty                                        regularization term: 'none', 'l2' , 'l1' , or 'elasticnet'
    max_cores                                      can be a number, or "auto".

TODO:
    predictor_tester.py <filename> <output_folder> sgd <loss> <penalty> <max_cores> [-i] [-v]
    predictor_tester.py <filename> <output_folder> passive-aggressive <loss> <max_cores> [-i] [-v]

'''
from base.docopt import docopt
from base.prototype import _job_input_to_job
from base.workload_parser import parse_lines
from base.np_printutils import array_to_file
from base.np_printutils import np_array_to_file
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
if arguments['<max_cores>']=="auto":
    with open(arguments['<filename>']) as input_file:
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
elif arguments['<max_cores>'].isdigit():
    num_processors=eval(arguments['<max_cores>'])
else:
    raise ValueError("<max_cores> must be an integer or \"auto\"")

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
with open(arguments['<filename>'], 'rt') as  f:
    jobs = _my_job_inputs_to_jobs(parse_lines(f), num_processors)
    print("Parsed swf file.")

    print("Choosing predictor.")
    if arguments["tsafrir"]:
        from predictors.predictor_tsafrir import PredictorTsafrir
        predictor=PredictorTsafrir()
    elif arguments["clairvoyant"]:
        from predictors.predictor_tsafrir import PredictorClairvoyant
        predictor=PredictorClairvoyant()
    elif arguments["sgd_linear"]:
        if arguments["<loss>"] not in ["squared_loss"]:
            raise ValueError("loss not supported. supported losses=%s"%(supported_losses.__str__()))
        if arguments["<penalty>"] not in ["none"]:
            raise ValueError("penalty not supported. supported penalties=%s"%(supported_penalties.__str__()))
        from predictors.predictor_sgdlinear import PredictorSGDLinear
        predictor=PredictorSGDLinear(max_runtime=None, loss=arguments["<loss>"], eta=0.01, regularization="l1",alpha=1,beta=0)
    else:
        raise ValueError("no valid predictor specified")
    iprint("Predictor created.")

    #Getting a simulation environment
    env = Environment()

    pred=[]
    def job_process(j):
        yield env.timeout(j.submit_time)
        predictor.predict(j,env.now)
        pred.append(j.predicted_run_time)
        yield env.timeout(j.wait_time+j.actual_run_time)
        predictor.fit(j,env.now)

    #Starting the replay
    for job in jobs:
        env.start(job_process(job))
    simulate(env)

    if arguments['--interactive']==True:
        print(arguments)
        from IPython import embed
        embed()

if arguments["tsafrir"]:
    array_to_file(pred,arguments["<output_folder>"]+"/prediction_tsafrir")
elif arguments["clairvoyant"]:
    array_to_file(pred,arguments["<output_folder>"]+"/prediction_clairvoyant")
elif arguments["sgd_linear"]:
    print(pred)
    np_array_to_file(pred[:4],arguments["<output_folder>"]+"/prediction_sgd_linear_loss:%s_penalty:%s_eta:%s_alpha:%s_beta:%s"%(arguments["<loss>"],arguments["<penalty>"],arguments["<eta>"],arguments["<alpha>"],arguments["<beta>"]))
else:
    raise ValueError("no valid predictor")
