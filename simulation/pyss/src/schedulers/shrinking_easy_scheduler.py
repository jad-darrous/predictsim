from common import CpuSnapshot
from easy_backfill_scheduler import EasyBackfillScheduler

import common_correctors
from base.prototype import JobStartEvent

class  ShrinkingEasyScheduler(EasyBackfillScheduler):
    """ This "toy" algorithm follows an the paper of Tsafrir, Etzion, Feitelson, june 2007
    """
    
    def __init__(self, options):
        super(ShrinkingEasyScheduler, self).__init__(options)
        print("WARNING: this scheduler (ShrinkingEasyScheduler) should be updated to work with predictor and corrector. The actual code only mimics previous behaviour (predictor=reqtime/2, corrector=reqtime)") 
        self.cpu_snapshot = CpuSnapshot(self.num_processors)
        self.unscheduled_jobs = []

    def new_events_on_job_submission(self, job, current_time):
	if job.user_estimated_run_time > 1: 
		job.predicted_run_time = int(job.user_estimated_run_time / 2)
	else: 
		job.predicted_run_time = 1 
        return super(ShrinkingEasyScheduler, self).new_events_on_job_submission(job, current_time)

    def new_events_on_job_under_prediction(self, job, current_time):
        assert job.predicted_run_time <= job.user_estimated_run_time
        new_predicted_run_time = common_correctors.reqtime(job, current_time)
        self.cpu_snapshot.assignTailofJobToTheCpuSlices(job, new_predicted_run_time)
        job.predicted_run_time = new_predicted_run_time
        return [JobStartEvent(current_time, job)]

