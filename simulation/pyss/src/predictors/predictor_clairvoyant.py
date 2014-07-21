from predictor import Predictor

class PredictorClairvoyant(Predictor):
	"""
	estimate_runtime = real runtime
	"""

        def __init__(self,max_procs=None, max_runtime=None, loss="squared_loss", eta=0.01, regularization="l1",alpha=1,beta=0,verbose=True):
		pass

	def predict(self, job, current_time):
		"""
		Modify the estimate_runtime of job.
		Called when a job is submitted to the system.
		"""
		job.predicted_run_time = job.actual_run_time

	def fit(self, job, current_time):
		pass
