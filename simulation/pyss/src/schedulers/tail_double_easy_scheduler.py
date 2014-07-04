from common import Scheduler, CpuSnapshot, list_copy 
from easy_scheduler import EasyBackfillScheduler

# This scheduler is similar to the standard easy scheduler. The only diffrence is that 
# the tail of jobs is doubled before the decision of backfilling.
# recall our default init assumption: job.predicted_run_time = job.user_estimated_run_time
 
class  TailDoubleEasyScheduler(EasyBackfillScheduler):
    """ This algorithm implements the algorithm in the paper of Tsafrir, Etzion, Feitelson, june 2007?
    """
    
    def __init__(self, num_processors):
        super(TailDoubleEasyScheduler, self).__init__(num_processors)
        self.cpu_snapshot = CpuSnapshot(num_processors)

    
    def _backfill_jobs(self, current_time):
        "Overriding parent method"
        if len(self.unscheduled_jobs) <= 1:
            return []

        result = []  
        first_job = self.unscheduled_jobs[0]        
        tail =  list_copy(self.unscheduled_jobs[1:]) 
        
        self.cpu_snapshot.assignJobEarliest(first_job, current_time)
        
        for job in tail:
            job.predicted_run_time = 2 * job.user_estimated_run_time # doubling is done here 
            if self.cpu_snapshot.canJobStartNow(job, current_time): # if job can be backfilled 
                self.unscheduled_jobs.remove(job)
                self.cpu_snapshot.assignJob(job, current_time)
                result.append(job)
            else:
                job.predicted_run_time = job.user_estimated_run_time # undoubling is done here 
                
        self.cpu_snapshot.delJobFromCpuSlices(first_job)

        return result

