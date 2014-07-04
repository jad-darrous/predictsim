from common import CpuSnapshot
from conservative_scheduler import ConservativeScheduler


#this scheduler only doubles the user estimation and then apply the regular Conservative Schedular

class DoubleConservativeScheduler(ConservativeScheduler):
    def __init__(self, num_processors, weights_list=None, weights_backfill=None):
        super(DoubleConservativeScheduler, self).__init__(num_processors)

    def new_events_on_job_submission(self, job, current_time):
        "Overriding parent method"
        job.predicted_run_time = 2 * job.user_estimated_run_time
        return super(DoubleConservativeScheduler, self).new_events_on_job_submission(job, current_time)

