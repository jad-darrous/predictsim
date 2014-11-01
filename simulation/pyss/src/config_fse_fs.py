#! /usr/bin/env python2


#The scheduler to use.
#To list them: for s in schedulers/*_scheduler.py ; do basename -s .py $s; done
scheduler = {
        "name":'energetic_fairshare_scheduler',
        "weights":{
                'size':0,
                'fairshare':1000000,
                'energeticfairshare':0
                }
        }

#the number of available processors in the simulated parallel machine
#num_processors = 80640

#should some stats have to be computed?
stats = False

output_swf_energy = True


