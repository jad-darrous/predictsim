
from abc import ABCMeta, abstractmethod


class SchedulingPerformanceMeasure:
	__metaclass__ = ABCMeta

	def __init__(self, fname=None, jobs=None):
		self.fname = fname
		self.jobs = jobs

	@abstractmethod
	def compute_job(self, wt, rt): pass

	@abstractmethod
	def compute_log(self): pass

	def compute_log(self):
		return None
		vals = []
		with open(self.fname, "rb") as f:
			for line in f.xreadlines():
				if not line.lstrip().startswith(';'):
					job = [float(v) for v in [u for u in line.strip().split()]]
					vals.append(self.compute_job(job));
		return vals

	def average(self):
		job_val = self.compute_log()
		return sum(job_val) / len(job_val)

	def median(self):
		job_val = self.compute_log()
		job_val.sort()
		return job_val[len(job_val)/2]

	def max(self):
		job_val = self.compute_log()
		return max(job_val)

	def all(self):
		job_val = self.compute_log()
		print len(job_val)
		job_val.sort()
		avg = sum(job_val) / len(job_val)
		med = job_val[len(job_val)/2]
		mxx = job_val[-1]
		return avg, med, mxx


class SlowdownMeasure(SchedulingPerformanceMeasure):

	def gen_vals_memory(self):
		for job in self.jobs:
			wt = float(job.start_to_run_at_time - job.submit_time)
			rt = float(job.actual_run_time)
			yield self.compute_job(wt, rt);

	def gen_vals_file(self):
		with open(self.fname, "rb") as f:
			for line in f.xreadlines():
				if not line.lstrip().startswith(';'):
					wt, rt = [float(v) for v in [u for u in line.strip().split()][2:4]]
					yield self.compute_job(wt, rt);

	def compute_log(self):
		# if self.jobs is not None:
		# 	g = gen_vals_memory
		# else:
		# 	g = gen_vals_file
		# return self.g()

		vals = []
		if self.jobs is not None:
			for job in self.jobs:
				wt = float(job.start_to_run_at_time - job.submit_time)
				rt = float(job.actual_run_time)
				vals.append(self.compute_job(wt, rt));
		else:
			with open(self.fname, "rb") as f:
				for line in f.xreadlines():
					if not line.lstrip().startswith(';'):
						wt, rt = [float(v) for v in [u for u in line.strip().split()][2:4]]
						vals.append(self.compute_job(wt, rt));
		return vals


class Slowdown(SlowdownMeasure):

	def compute_job(self, wt, rt):
		return (wt+rt)/rt

	def __str__(self):
		return "Standard-Slowdown"


class BoundedSlowdown(SlowdownMeasure):
	tau = 10.0

	def compute_job(self, wt, rt):
		return max((wt+rt)/max(rt, BoundedSlowdown.tau), 1)

	def __str__(self):
		return "Bounded-Slowdown with tau=" + str(BoundedSlowdown.tau)

