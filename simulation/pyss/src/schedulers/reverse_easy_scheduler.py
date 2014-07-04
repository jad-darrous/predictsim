from common import Scheduler, CpuSnapshot, list_copy
from easy_scheduler import EasyBackfillScheduler

# latest job first 
latest_sort_key = (
    lambda job :  -job.submit_time
)

# this scheduler is similar to the standard easy scheduler. The only diffrence is that 
# the tail of jobs is reordered by reverse order of submission before trying to backfill jobs in the tail.
  
class  ReverseEasyScheduler(EasyBackfillScheduler):
    
    def __init__(self, num_processors):
        super(ReverseEasyScheduler, self).__init__(num_processors)
        self.cpu_snapshot = CpuSnapshot(num_processors)

    
    def _backfill_jobs(self, current_time):
        "Overriding parent method"
        if len(self.unscheduled_jobs) <= 1:
            return []

        result = []  
        first_job = self.unscheduled_jobs[0]        
        tail =  list_copy(self.unscheduled_jobs[1:])
        tail_of_jobs_by_reverse_order = sorted(tail, key=latest_sort_key)
        
        self.cpu_snapshot.assignJobEarliest(first_job, current_time)
        
        for job in tail_of_jobs_by_reverse_order:
            if self.cpu_snapshot.canJobStartNow(job, current_time): 
                self.unscheduled_jobs.remove(job)
                self.cpu_snapshot.assignJob(job, current_time)
                result.append(job)
                
        self.cpu_snapshot.delJobFromCpuSlices(first_job)

        return result
    
