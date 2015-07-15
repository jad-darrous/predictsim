from predictor import Predictor

class PredictorMy(Predictor):

	def __init__(self, options):
		pass

	def predict(self, job, current_time, list_running_jobs):
		job.predicted_run_time = job.user_estimated_run_time/10.0

	def fit(self, job, current_time):
		pass
