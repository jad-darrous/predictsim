#! /usr/bin/env python2


#The scheduler to use.
#To list them: for s in schedulers/*_scheduler.py ; do basename -s .py $s; done
scheduler = {
	"name":'maui_scheduler'
}

#the number of available processors in the simulated parallel machine
num_processors = 80640
num_processors = 2


#should some stats have to be computed?
stats = False

weights = (1, 0, 0, 0, 0, 0)
