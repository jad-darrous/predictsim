"""
Correctors.
When an underprediction occurs, what to do ? The prediction have to be coorected.
In this file, you will find a collection of corrector.

"""

def correctors_list():
	return ["reqtime","tsafrir","ninetynine","wait","recursive_doubling"]

#reqtime (assume reqtime if runtime >prediction)
def reqtime(job, current_time):
	new_predicted_run_time = job.user_estimated_run_time
	return new_predicted_run_time




#tsafrir(if runtime > prediction, then +1mn, +2mn,+5mn,+10mn.. cf papier),
def tsafrir(job, current_time):
	if(not hasattr(job, "number_of_corrections")):
		job.number_of_corrections = 0
	time_correction = [0, 60, 60*5, 60*15, 60*30, 3600, 3600*2, 3600*5, 3600*10, 3600*20, 3600*50, 3600*100]
	if(job.number_of_corrections >= len(time_correction)):
		print("Corrector Tsafrir: not enough time_correction!")
		return job.user_estimated_run_time
	new_predicted_run_time = job.predicted_run_time - time_correction[job.number_of_corrections]
	job.number_of_corrections += 1
	new_predicted_run_time += time_correction[job.number_of_corrections]
	new_predicted_run_time = min(new_predicted_run_time, job.user_estimated_run_time)
	return new_predicted_run_time

#if runtime>prediction, then "99% of jobs are shorter than" value,
def ninetynine(pestimator,job, current_time):
	if(not hasattr(job, "corrected")):
            job.corrected = True
            v=abs(1+pestimator.estimate()*job.user_estimated_run_time)
            return int(min(job.predicted_run_time+v,job.user_estimated_run_time))
        else:
            return job.user_estimated_run_time

#"wait"(stop backfilling (and scheduling) as soon as "shadow" reservation is delayed)
def wait(job, current_time):
	print("TODO")
	return job.user_estimated_run_time



#recursive doubling: we double the time
def recursive_doubling(job, current_time):
	new_predicted_run_time = job.predicted_run_time * 2
	return new_predicted_run_time

