from predictor import Predictor

class PredictorDoubleClairvoyant(Predictor):
	"""
	estimate_runtime = real runtime
	"""

        def __init__(self, options):
		pass

	def predict(self, job, current_time, list_running_jobs):
                """
                Modify the predicted_run_time of a job.
                Called when a job is submitted to the system.
                """
		job.predicted_run_time = job.actual_run_time * 2

	def fit(self, job, current_time):
		"""
		Add a job to the learning algorithm.
		Called when a job end.
		"""
		pass
