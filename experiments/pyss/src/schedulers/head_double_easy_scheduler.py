from common import Scheduler, CpuSnapshot
from easy_scheduler import EasyBackfillScheduler

# This scheduler is similar to the standard easy scheduler. The only diffrence is that 
# the _head_ of jobs is doubled before the decision of backfilling.
# recall our default init assumption: job.predicted_run_time = job.user_estimated_run_time



class HeadDoubleEasyScheduler(EasyBackfillScheduler):

    def __init__(self, num_processors):
        super(HeadDoubleEasyScheduler, self).__init__(num_processors)
        self.cpu_snapshot = CpuSnapshot(num_processors)


    def _schedule_head_of_list(self, current_time):
        "Overriding parent method"

        result = []
        while True:
            if len(self.unscheduled_jobs) == 0:
                break
            # check if the first job can be scheduled at current time
            if self.cpu_snapshot.free_processors_available_at(current_time) >= self.unscheduled_jobs[0].num_required_processors:
                job = self.unscheduled_jobs.pop(0)
		job.predicted_run_time = 2 * job.user_estimated_run_time # doubling is done here  
                self.cpu_snapshot.assignJob(job, current_time)
                result.append(job)
            else:
                # first job can't be scheduled
                break
        return result

