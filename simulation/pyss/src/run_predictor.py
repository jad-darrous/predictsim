#!/usr/bin/python
# encoding: utf-8
'''
Runtime predictor tester.

Usage:
    predictor_tester.py <filename> <output_folder> tsafrir <max_cores> [-i] [-v]
    predictor_tester.py <filename> <output_folder> clairvoyant <max_cores> [-i] [-v]

Options:
    -h --help                                      Show this help message and exit.
    -v --verbose                                   Be verbose.
    -i --interactive                               Interactive mode after script.
    tool                                           the machine learning technique to use. available: sgd,passive-aggressive,tsafrir.
    encoding                                       how to encode discret attributes (s.t. user ID). available: continuous, onehot.
    loss                                           for sgd: in  'squared_loss', 'huber', 'epsilon_insensitive', 'squared_epsilon_insensitive', 'maeloss'.
                                                   for passive-aggressive: in 'epsilon_insensitive', 'squared_epsilon_insensitive'
    penalty                                        in 'l2' , 'l1' , 'elasticnet'
    max_cores                                      can be a number, or "auto".

TODO:
    predictor_tester.py <filename> <output_folder> sgd <loss> <penalty> <max_cores> [-i] [-v]
    predictor_tester.py <filename> <output_folder> passive-aggressive <loss> <max_cores> [-i] [-v]

'''
from base.docopt import docopt
from base.prototype import _job_input_to_job
from base.workload_parser import parse_lines
from base.np_printutils import array_to_file
from simpy import Environment,simulate,Monitor
from simpy.util import start_delayed

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
            raise ValueError("missing num processors")
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
    predictor=None
    if arguments["tsafrir"]:
        from predictors.predictor_tsafrir import PredictorTsafrir
        predictor=PredictorTsafrir(num_processors)
    if arguments["clairvoyant"]:
        from predictors.predictor_tsafrir import PredictorClairvoyant
        predictor=PredictorClairvoyant(num_processors)
    if predictor==None:
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
if arguments["clairvoyant"]:
    array_to_file(pred,arguments["<output_folder>"]+"/prediction_clairvoyant")
