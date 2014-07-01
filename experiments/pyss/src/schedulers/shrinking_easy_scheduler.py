from common import CpuSnapshot
from easy_scheduler import EasyBackfillScheduler

class  ShrinkingEasyScheduler(EasyBackfillScheduler):
    """ This "toy" algorithm follows an the paper of Tsafrir, Etzion, Feitelson, june 2007
    """
    
    def __init__(self, num_processors):
        super(ShrinkingEasyScheduler, self).__init__(num_processors)
        self.cpu_snapshot = CpuSnapshot(num_processors)
        self.unscheduled_jobs = []

    def new_events_on_job_submission(self, job, current_time):
	if job.user_estimated_run_time > 1: 
		job.predicted_run_time = int(job.user_estimated_run_time / 2)
	else: 
		job.predicted_run_time = 1 
        return super(ShrinkingEasyScheduler, self).new_events_on_job_submission(job, current_time)

    def new_events_on_job_under_prediction(self, job, current_time):
        assert job.predicted_run_time <= job.user_estimated_run_time
        self.cpu_snapshot.assignTailofJobToTheCpuSlices(job) 
        return []

