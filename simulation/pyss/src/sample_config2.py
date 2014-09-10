#! /usr/bin/env python2


#The scheduler to use.
#To list them: for s in schedulers/*_scheduler.py ; do basename -s .py $s; done
scheduler = {
	"name":'easy_plus_plus_scheduler',
	
	#The predictor (if needed) to use.
	#To list them: for s in predictors/predictor_*.py ; do basename -s .py $s; done
	'predictor': {"name":"predictor_tsafrir", "option1":"bar"},
	
	#The corrector (if needed) to use.
	#Choose between: "+str(schedulers.common_correctors.correctors_list())
	'corrector': {"name":"tsafrir", "option1":"foo"},

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
Wait (Tw) [minutes]:  63.8220180529
Response time (Tw+Tr) [minutes]:  186.442337711
Slowdown (Tw+Tr) / Tr:  438.943506263
Bounded slowdown max(1, (Tw+Tr) / max(10, Tr):  71.2782829212
Estimated slowdown (Tw+Tr) / Te:  350.31818206
Tail slowdown (if bounded_sld >= 3):  536.229754526
   Number of jobs in the tail:  1289
Tail Percentile (the top 10% sld):  4371.72912372
Total Number of jobs:  9924
Number of jobs used to calculate statistics:  9823

Num of Processors:  80640
Input file:  ../../../data/CEA-curie_sample/original_swf/log.swf
Scheduler: <class 'schedulers.easy_plus_plus_scheduler.EasyPlusPlusScheduler'>
"""

