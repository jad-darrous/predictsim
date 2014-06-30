from easy_plus_plus_scheduler import EasyPlusPlusScheduler
from base.prototype import JobStartEvent

class  AlphaEasyScheduler(EasyPlusPlusScheduler):
    """ This algorithm inspired by the algorithm in the paper of Tsafrir, Etzion, Feitelson, june 2007
        Here we use as the prediction (instea d of the average of the last two reecnt user jobs)
	 the parameter alpha that denotes how the user is precise (in "average") in his estimation 
    """
    
    def __init__(self, num_processors):
        super(AlphaEasyScheduler, self).__init__(num_processors)
	self.user_jobs = {}
    
    def new_events_on_job_submission(self, job, current_time):
        if not self.user_jobs.has_key(job.user_id): 
            self.user_jobs[job.user_id] = []
            
        self.cpu_snapshot.archive_old_slices(current_time)
        self.unscheduled_jobs.append(job)
        return [
            JobStartEvent(current_time, job)
            for job in self._schedule_jobs(current_time)
        ]


    def new_events_on_job_termination(self, job, current_time):
        assert self.user_jobs.has_key(job.user_id) == True
 
        self.user_jobs[job.user_id].append(job)
        self.cpu_snapshot.archive_old_slices(current_time)
        self.cpu_snapshot.delTailofJobFromCpuSlices(job)
        return [
            JobStartEvent(current_time, job)
            for job in self._schedule_jobs(current_time)
        ]


    def _schedule_jobs(self, current_time):
        "Schedules jobs that can run right now, and returns them"
   
        for job in self.unscheduled_jobs:
            if self.user_jobs[job.user_id] != []: 
                alpha =  self.calculate_alpha(self.user_jobs[job.user_id])
                job.predicted_run_time = max (1, int (alpha * job.user_estimated_run_time))  

        jobs  = self._schedule_head_of_list(current_time)
        jobs += self._backfill_jobs(current_time)
        return jobs

    
    def calculate_alpha (self, user_list_of_jobs): # calculates the average of the precision of the user estimation

        result = 0.0 
        for job in user_list_of_jobs:
            result += float(job.actual_run_time) / job.user_estimated_run_time

        return result / len(user_list_of_jobs)

 
