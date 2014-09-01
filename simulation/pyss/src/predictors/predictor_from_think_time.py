from predictor import Predictor

class PredictorFromThinkTime(Predictor):
	"""
	estimate_runtime = think time
	"""

        def __init__(self,max_procs=None, max_runtime=None, loss="squared_loss", eta=0.01, regularization="l1",alpha=1,beta=0,verbose=True):
		pass

	def predict(self, job, current_time):
		"""
		Modify the estimate_runtime of job.
		Called when a job is submitted to the system.
		"""
		if job.think_time > 0:
			job.predicted_run_time = job.think_time
		else:
			job.predicted_run_time = job.user_estimated_run_time

	def fit(self, job, current_time):
		pass
