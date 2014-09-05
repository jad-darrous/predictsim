from predictor import Predictor

class PredictorReqtime(Predictor):
	"""
	estimate_runtime = user value
	"""

        def __init__(self, options):
		pass

	def predict(self, job, current_time, list_running_jobs):
                """
                Modify the predicted_run_time of a job.
                Called when a job is submitted to the system.
                """
		job.predicted_run_time = job.user_estimated_run_time

	def fit(self, job, current_time):
		"""
		Add a job to the learning algorithm.
		Called when a job end.
		"""
		pass
