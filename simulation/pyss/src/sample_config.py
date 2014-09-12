#! /usr/bin/env python2


#The scheduler to use.
#To list them: for s in schedulers/*_scheduler.py ; do basename -s .py $s; done
scheduler = {
	"name":'easy_backfill_scheduler',

	#The predictor (if needed) to use.
	#To list them: for s in predictors/predictor_*.py ; do basename -s .py $s; done
	'predictor': {"name":None, "option1":"bar"},

	#The corrector (if needed) to use.
	#Choose between: "+str(schedulers.common_correctors.correctors_list())
	'corrector': {"name":None, "option1":"foo"},

	"more_option":"foo"
	}

#a file in the standard workload format: http://www.cs.huji.ac.il/labs/parallel/workload/swf.html
# if '-' read from stdin
input_file = '../../../data/CEA-curie_sample/original_swf/log.swf'

#the number of available processors in the simulated parallel machine
num_processors = 80640

#should some stats have to be computed?
stats = True

#if set, create a swf file of the run
output_swf = 'res.swf'


"""
should output:

WARINING: [..]
[..]

STATISTICS:
Wait (Tw) [minutes]:  61.5191506329
Response time (Tw+Tr) [minutes]:  184.139470291
Slowdown (Tw+Tr) / Tr:  405.583038621
Bounded slowdown max(1, (Tw+Tr) / max(10, Tr):  63.930142519
Estimated slowdown (Tw+Tr) / Te:  306.14067403
Tail slowdown (if bounded_sld >= 3):  419.9131661
   Number of jobs in the tail:  1474
Tail Percentile (the top 10% sld):  4036.43339341
Total Number of jobs:  9924
Number of jobs used to calculate statistics:  9823

Num of Processors:  80640
Input file:  ../../../data/CEA-curie_sample/original_swf/log.swf
Scheduler: <class 'schedulers.easy_scheduler.EasyBackfillScheduler'>
"""

