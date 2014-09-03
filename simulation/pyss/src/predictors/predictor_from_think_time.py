from predictor import Predictor

class PredictorFromThinkTime(Predictor):
	"""
	estimate_runtime = think time
	"""

        def __init__(self,config_dict):
		pass

	def predict(self, job, current_time, list_running_jobs):
                """
                Modify the predicted_run_time of a job.
                Called when a job is submitted to the system.
                """
		if job.think_time > 0:
			job.predicted_run_time = job.think_time
		else:
			job.predicted_run_time = job.user_estimated_run_time

	def fit(self, job, current_time):
		"""
		Add a job to the learning algorithm.
		Called when a job end.
		"""
		pass
