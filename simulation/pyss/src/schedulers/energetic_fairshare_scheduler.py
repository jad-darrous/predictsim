from common import Scheduler, CpuSnapshot, list_copy 
from base.prototype import JobStartEvent


class Weights(object):
	# this class defines the configuration of weights
	def __init__(self, w_size=0.0, fs=0.0, fse=0.0):
		self.size   = w_size   # weight of job size (= num_required_processors)
		self.fairshare   = fs   #fs
		self.energeticfairshare   = fse   #fse

	def __str__(self):
		return( "class Weights(w_wtime=%i, w_size=%i, fs=%i, fse=%i)" %
			(self.wtime, self.size, self.fairshare , self.energeticfairshare))


class EnergeticFairshareScheduler(Scheduler):
	def __init__(self, options):
		super(EnergeticFairshareScheduler, self).__init__(options)
		self.cpu_snapshot = CpuSnapshot(self.num_processors)
		self.unscheduled_jobs = []
		
		#there is a bug in self.cpu_snapshot.free_processors_available_at(current_time)
		self.free_processors = self.num_processors
		
		self.num_processors = float(self.num_processors)
		
		self.user_cputime_counter = {}
		self.user_cputime_max = 0.000001
		self.user_energy_counter = {}
		self.user_energy_max = 0.000001
		
		
		
		if "weights" in options["scheduler"]:
			self.weights = Weights(
				float(options["scheduler"]["weights"]["size"]),
				float(options["scheduler"]["weights"]["fairshare"]),
				float(options["scheduler"]["weights"]["energeticfairshare"]))
		else:
			self.weights = Weights()
		

	def new_events_on_job_submission(self, just_submitted_job, current_time):
		if not self.user_cputime_counter.has_key(just_submitted_job.user_id):
			self.user_cputime_counter[just_submitted_job.user_id] = 0.0
			self.user_energy_counter[just_submitted_job.user_id] = 0.0
		
		""" Here we first add the new job to the waiting list. We then try to schedule
		the jobs in the waiting list, returning a collection of new termination events """
		# TODO: a probable performance bottleneck because we reschedule all the
		# jobs. Knowing that only one new job is added allows more efficient
		# scheduling here.
		self.cpu_snapshot.archive_old_slices(current_time)
		self.unscheduled_jobs.append(just_submitted_job)
		
		retl = []
		
		assert self.free_processors <= self.cpu_snapshot.free_processors_available_at(current_time)
		if (self.free_processors >= just_submitted_job.num_required_processors):
			for job in self._schedule_jobs(current_time):
				retl.append(JobStartEvent(current_time, job))
		
		return retl

	def _schedule_jobs(self, current_time):
		#print("<start job sched @ %i>"%current_time)
		"Overriding parent method"
		#print ("cputime at %i: "%current_time, self.user_cputime_counter)
		#print ("energy  at %i: "%current_time, self.user_energy_counter, "// free: %i VS %i"%(self.cpu_snapshot.free_processors_available_at(current_time), self.free_processors))
		self.unscheduled_jobs.sort(
			key = lambda x: self.waiting_list_weight(x, current_time)
			#reverse=True
		)
		#print self.unscheduled_jobs
		#for i in self.unscheduled_jobs:
			#print ("%i @ %i (user:%i) SCORE: "%(i.id,current_time,i.user_id), self.waiting_list_weight(i, current_time))

		"Schedules jobs that can run right now, and returns them"
		jobs = self._schedule_head_of_list(current_time)
		jobs += self._backfill_jobs(current_time)


		#for i in jobs:
			#print "START OF %i @ %i (user:%i) // free:%i VS %i"%(i.id,current_time,i.user_id,self.cpu_snapshot.free_processors_available_at(current_time), self.free_processors)
		#print a
		#print("<end   job sched @ %i>"%current_time)
		return jobs



	def waiting_list_weight(self, job, current_time):

		return (
		self.weights.size   * (1.0 - float(job.num_required_processors)/self.num_processors) +
		self.weights.fairshare   * (self.user_cputime_counter[job.user_id]/self.user_cputime_max) +
		self.weights.energeticfairshare   * (self.user_energy_counter[job.user_id]/self.user_energy_max)
		,job.submit_time # when 2 jobs have the same score, we sort them FIFO.
		)
	
	def new_events_on_job_termination(self, job, current_time):
		
		self.free_processors += job.num_required_processors
		
		
		self.user_cputime_counter[job.user_id] += float(job.actual_run_time * job.num_required_processors)
		self.user_energy_counter[job.user_id] += float(job.energy)
		
		if self.user_cputime_counter[job.user_id] > self.user_cputime_max:
			self.user_cputime_max = self.user_cputime_counter[job.user_id]
		if self.user_energy_counter[job.user_id] > self.user_energy_max:
			self.user_energy_max = self.user_energy_counter[job.user_id]
		
		#print "END   OF %i @ %i (user:%i) // free:%i VS %i"%(job.id,current_time,job.user_id,self.cpu_snapshot.free_processors_available_at(current_time), self.free_processors)
		
		
		""" Here we first delete the tail of the just terminated job (in case it's
		done before user estimation time). We then try to schedule the jobs in the waiting list,
		returning a collection of new termination events """
		self.cpu_snapshot.archive_old_slices(current_time)
		self.cpu_snapshot.delTailofJobFromCpuSlices(job)
		return [
			JobStartEvent(current_time, job)
			for job in self._schedule_jobs(current_time)
		]
		

	def _schedule_head_of_list(self, current_time):     
		result = []
		while True:
			if len(self.unscheduled_jobs) == 0:
				break
			# Try to schedule the first job
			assert self.free_processors <= self.cpu_snapshot.free_processors_available_at(current_time)
			if self.free_processors >= self.unscheduled_jobs[0].num_required_processors:
				job = self.unscheduled_jobs.pop(0)
				self.cpu_snapshot.assignJob(job, current_time)
				self.free_processors -= job.num_required_processors
				result.append(job)
			else:
				# first job can't be scheduled
				break
		return result

	def _backfill_jobs(self, current_time):
		"""
		Find jobs that can be backfilled and update the cpu snapshot.
		"""
		if len(self.unscheduled_jobs) <= 1:
			return []
		
		result = []


		tail_of_waiting_list = list_copy(self.unscheduled_jobs[1:])
		
		for job in tail_of_waiting_list:
			if self.canBeBackfilled(job, current_time):
				self.unscheduled_jobs.remove(job)
				self.cpu_snapshot.assignJob(job, current_time)
				self.free_processors -= job.num_required_processors
				result.append(job)

		return result 

	def canBeBackfilled(self, second_job, current_time):
		assert len(self.unscheduled_jobs) >= 2
		assert second_job in self.unscheduled_jobs[1:]
		
		assert self.free_processors <= self.cpu_snapshot.free_processors_available_at(current_time)
		if self.free_processors < second_job.num_required_processors:
			return False

		first_job = self.unscheduled_jobs[0]

		self.cpu_snapshot.assignJobEarliest(first_job, current_time)
		self.free_processors -= first_job.num_required_processors
		
		# if true, this means that the 2nd job is "independent" of the 1st, and thus can be backfilled
		ret = self.cpu_snapshot.canJobStartNow(second_job, current_time)

		#undo things
		self.cpu_snapshot.unAssignJob(first_job)
		self.free_processors += first_job.num_required_processors
		
		return ret


   


