from common import CpuSnapshot, list_copy 
from easy_scheduler import EasyBackfillScheduler

def default_score_function(job):
    return job.num_required_processors * job.user_estimated_run_time


class Entry(object):
    def __init__(self, cpu_snapshot = None):
        self.utilization = 0
        self.cpu_snapshot = cpu_snapshot

    def __str__(self):
        return '%d' % (self.utilization)


        
class LookAheadEasyBackFillScheduler(EasyBackfillScheduler):
    """
    
    This scheduler implements the LOS Scheduling Algorithm [Edi Shmueli and Dror Feitelson, 2005]
    It uses a dynamic programing method to decide which subset of jobs to backfill.
    The implemelmentation of this scheduler is based mainly on the EasyBackfillScheduler class.
    The single difference is that we only overide the _backfill_jobs function.
    This function calls the function _mark_jobs_in_look_ahead_best_order before the preforming backfilling itself.
    """
    
    def __init__(self, num_processors, score_function = None):
        super(LookAheadEasyBackFillScheduler, self).__init__(num_processors)

        if score_function is None:
            self.score_function = default_score_function
        else:
            self.score_function = score_function


    def _backfill_jobs(self, current_time):
        "Overriding parent method"
        if len(self.unscheduled_jobs) <= 1:
            return []

        self._mark_jobs_in_look_ahead_best_order(current_time)

        result = []
        tail_of_waiting_list = list_copy(self.unscheduled_jobs[1:])
        for job in tail_of_waiting_list:
            if job.backfill_flag == 1:
                self.unscheduled_jobs.remove(job)
                self.cpu_snapshot.assignJob(job, current_time)
                result.append(job)

        return result



    def _mark_jobs_in_look_ahead_best_order(self, current_time):
        assert self.cpu_snapshot.slices[0].start_time == current_time

        free_processors = self.cpu_snapshot.free_processors_available_at(current_time)
        first_job = self.unscheduled_jobs[0]
        cpu_snapshot_with_first_job = self.cpu_snapshot.quick_copy()
        cpu_snapshot_with_first_job.assignJobEarliest(first_job, current_time)
         

        # M[j, k] represents the subset of jobs in {0...j} with the highest utilization if k processors are available
        M = {}  
        
        for k in range(free_processors + 1): 
            M[-1, k] = Entry(cpu_snapshot_with_first_job.copy())

        for j in range(len(self.unscheduled_jobs)):
            job = self.unscheduled_jobs[j]
            assert job.backfill_flag == 0 
            for k in range(free_processors + 1):
                M[j, k] = Entry()
                M[j, k].utilization  =  M[j-1, k].utilization
                M[j, k].cpu_snapshot =  M[j-1, k].cpu_snapshot.copy()

                if (k < job.num_required_processors):
                    continue
                
                tmp_cpu_snapshot = M[j-1, k-job.num_required_processors].cpu_snapshot.copy()
                if tmp_cpu_snapshot.canJobStartNow(job, current_time):
                    tmp_cpu_snapshot.assignJob(job, current_time)
                else:
                    continue
                
                U1 = M[j, k].utilization 
                U2 = M[j-1, k-job.num_required_processors].utilization + self.score_function(job) 

                if U1 <= U2:
                    M[j, k].utilization = U2
                    M[j, k].cpu_snapshot = tmp_cpu_snapshot
                    

        best_entry = M[len(self.unscheduled_jobs) - 1, free_processors]
        for job in self.unscheduled_jobs:
            if job.id in best_entry.cpu_snapshot.slices[0].job_ids:        
                job.backfill_flag = 1  

        


