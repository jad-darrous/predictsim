#! /usr/bin/env python2


#The scheduler to use.
#To list them: for s in schedulers/*_scheduler.py ; do basename -s .py $s; done
scheduler = {
	"name":'easy_backfill_scheduler'
	}

#a file in the standard workload format: http://www.cs.huji.ac.il/labs/parallel/workload/swf.html
# if '-' read from stdin
input_file = '../../../data/CEA-curie_sample/original_swf/log.swf'

#the number of available processors in the simulated parallel machine
num_processors = 80640

#should some stats have to be computed?
stats = False

#if set, create a swf file of the run
output_swf = 'res.swf'


