from common import Scheduler, CpuSnapshot, list_copy
from easy_scheduler import EasyBackfillScheduler

# shortest job first 
sjf_sort_key = (
    lambda job :  job.predicted_run_time
)

# this scheduler is similar to the standard easy scheduler. The only diffrence is that 
# the tail of jobs is reordered by shortest job first before trying to backfill jobs in the tail.
  
class  EasySJBFScheduler(EasyBackfillScheduler):
    """ This algorithm implements the algorithm in the paper of Tsafrir, Etzion, Feitelson, june 2007?
    """
    
    def __init__(self, num_processors):
        super(EasySJBFScheduler, self).__init__(num_processors)
        self.cpu_snapshot = CpuSnapshot(num_processors)

    
    def _backfill_jobs(self, current_time):
        "Overriding parent method"
        if len(self.unscheduled_jobs) <= 1:
            return []

        result = []  
        first_job = self.unscheduled_jobs[0]        
        tail =  list_copy(self.unscheduled_jobs[1:])
        tail_of_jobs_by_sjf_order = sorted(tail, key=sjf_sort_key)
        
        self.cpu_snapshot.assignJobEarliest(first_job, current_time)
        
        for job in tail_of_jobs_by_sjf_order:
            if self.cpu_snapshot.canJobStartNow(job, current_time): 
                self.unscheduled_jobs.remove(job)
                self.cpu_snapshot.assignJob(job, current_time)
                result.append(job)
                
        self.cpu_snapshot.delJobFromCpuSlices(first_job)

        return result

