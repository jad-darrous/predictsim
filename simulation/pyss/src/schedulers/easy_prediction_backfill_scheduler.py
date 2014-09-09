from common import CpuSnapshot
from easy_backfill_scheduler import EasyBackfillScheduler
from base.prototype import JobStartEvent




class EasyPredictionBackfillScheduler(EasyBackfillScheduler):
	"""
	Easy Backfill scheduler with prediction and correction
	"""
	
	I_NEED_A_PREDICTOR = True
	
	def __init__(self, options):
		self.init_predictor(options)
		self.init_corrector(options)
		super(EasyPredictionBackfillScheduler, self).__init__(options)


	def new_events_on_job_submission(self, job, current_time):
		"Overriding parent method"
		self.predictor.predict(job, current_time, self.cpu_snapshot.jobs_at(current_time))
		return super(EasyPredictionBackfillScheduler, self).new_events_on_job_submission(job, current_time)

	# If you uncomment this, the prediction is called several time, just before a possible schedule for the job. 
	#This is how easy_+_+ is currently coded.
	#def _schedule_jobs(self, current_time):
		#"Overriding parent method"
		#for job in self.unscheduled_jobs:
			#self.predictor.predict(job, current_time, self.cpu_snapshot.jobs_at(current_time))
		#return super(EasyPredictionBackfillScheduler, self)._schedule_jobs(current_time)


	def new_events_on_job_termination(self, job, current_time):
		"Overriding parent method"
		self.predictor.fit(job, current_time)
		return super(EasyPredictionBackfillScheduler, self).new_events_on_job_termination(job, current_time)


	def new_events_on_job_under_prediction(self, job, current_time):
		assert job.predicted_run_time <= job.user_estimated_run_time

		new_predicted_run_time = self.corrector(job, current_time)

		#set the new predicted runtime
		self.cpu_snapshot.assignTailofJobToTheCpuSlices(job, new_predicted_run_time)
		job.predicted_run_time = new_predicted_run_time
		
		return [JobStartEvent(current_time, job)]