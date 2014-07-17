class Predictor(object):
	"""
	This is an "interface" to declare a predictor
	"""

	def __init__(self, num_processors, max_runtime=None):
		print("Do it")

	def predict(self, job, current_time):
		"""
		Return the estimate_runtime of job.
		Called when a job is submitted to the system.
		"""
		print("Do it")

	def fit(self, job, current_time):
		"""
		Add a job to the learning algorithm.
		Called when a job end.
		"""
		print("Do it")
