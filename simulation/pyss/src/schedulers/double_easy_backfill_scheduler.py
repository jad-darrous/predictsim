from common import CpuSnapshot
from easy_backfill_scheduler import EasyBackfillScheduler


#this scheduler only doubles the user estimation and then apply the regular Easy Backfill Scheduler

class DoubleEasyBackfillScheduler(EasyBackfillScheduler):
    def __init__(self, options):
        super(DoubleEasyBackfillScheduler, self).__init__(options)

    def new_events_on_job_submission(self, job, current_time):
        "Overriding parent method"
        job.predicted_run_time = 2 * job.user_estimated_run_time
        return super(DoubleEasyBackfillScheduler, self).new_events_on_job_submission(job, current_time)

