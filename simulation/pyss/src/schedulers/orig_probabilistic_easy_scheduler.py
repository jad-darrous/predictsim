from common import Scheduler, CpuSnapshot, list_copy
from base.prototype import JobStartEvent


def _round_time_up(num):
    assert num >= 0
    result = 1
    while result < num:
        result *= 2 
    return result


def _round_time_down(num):
    assert num >= 0
    if num == 0:
        return 0 
    result = 1
    while True:
        tmp = result*2
        if tmp <= num: 
            result = tmp
        else:
            break        
    return result

    
class Distribution(object):
    def __init__(self, job, window_size = 150):
        self.bins     = {}
        self.bins[1]  = 1 # adding the first entry to the main data structure of the distribution 
        self.number_of_jobs_added = 1
        self.number_of_actual_jobs_added = 0 
        
        self.window_size = window_size # the distribution contains information about at most window_size (recently terminated) jobs    
        self.jobs     = []


    def touch(self, rounded_up_time):
        curr_time = rounded_up_time
        while True:
            if curr_time in self.bins:
                break
            self.bins[curr_time] = 1  
            self.number_of_jobs_added += 1            
            curr_time /=  2


    def add_job(self, job): #to be called when a termination event has occured
        #Assumption: there exists a bin with a key value equals to rounded_up_run_time (see below).  
        assert job.user_estimated_run_time >= job.actual_run_time > 0
        rounded_up_run_time = _round_time_up(job.actual_run_time)

        self.number_of_jobs_added += 1
        self.number_of_actual_jobs_added += 1
        
        self.bins[rounded_up_run_time] += 1 # incrementing the numbers of terminated jobs encountered so far
        
        self.jobs.append(job)
        if len(self.jobs) > self.window_size:
            self.del_job(self.jobs.pop(0))
        

    def del_job(self, job):
        rounded_up_run_time = _round_time_up(job.actual_run_time)
	assert self.number_of_jobs_added >= self.bins[rounded_up_run_time] > 0
   
        self.number_of_jobs_added -= 1
        self.bins[rounded_up_run_time] -= 1


    def expected_run_time(self, job):
        key_value_sum = value_sum = 0 
        for (key,value) in self.bins.iteritems():
            if key <= job.user_estimated_run_time:
                key_value_sum  += (key * value)
		value_sum += value 
		 
        result = (float(key_value_sum) / value_sum)
        return result

        

class  OrigProbabilisticEasyScheduler(Scheduler):
    """ This algorithm implements a version of Feitelson and Nissimov, June 2007 
    """
    
    def __init__(self, num_processors, threshold = 0.2, window_size=150):
        super(OrigProbabilisticEasyScheduler, self).__init__(num_processors)
        self.threshold    = threshold
        self.window_size  = window_size # a parameter for the distribution 
        self.cpu_snapshot = CpuSnapshot(num_processors)
        
        self.user_distribution = {}

        self.unscheduled_jobs  = []
        self.currently_running_jobs = []
     
        #self.work_list = [[None for i in xrange(self.num_processors+1)] for j in xrange(self.num_processors+1)]
        self.M = {}        
        for c in xrange(self.num_processors+1):
            for n in xrange(self.num_processors+1):
                self.M[c, n] = 0.0

        self.max_user_rounded_estimated_run_time = 0
        self.prev_max_user_rounded_estimated_run_time = 0

        

    def new_events_on_job_submission(self, job, current_time):
        # print "arrived:", job
        rounded_up_estimated_time = _round_time_up(job.user_estimated_run_time)

        if  rounded_up_estimated_time > self.max_user_rounded_estimated_run_time:
            self.prev_max_user_rounded_estimated_run_time = self.max_user_rounded_estimated_run_time
            self.max_user_rounded_estimated_run_time = rounded_up_estimated_time
    
        if  not self.user_distribution.has_key(job.user_id):
            self.user_distribution[job.user_id] = Distribution(job, self.window_size)
        self.user_distribution[job.user_id].touch(2*self.max_user_rounded_estimated_run_time)

        if  self.prev_max_user_rounded_estimated_run_time < self.max_user_rounded_estimated_run_time:
            for tmp_job in self.currently_running_jobs:
                self.user_distribution[tmp_job.user_id].touch(2*self.max_user_rounded_estimated_run_time)
              
        self.cpu_snapshot.archive_old_slices(current_time)
        self.unscheduled_jobs.append(job)
        return [
            JobStartEvent(current_time, job)
            for job in self._schedule_jobs(current_time)
        ]


    def new_events_on_job_termination(self, job, current_time):
        self.user_distribution[job.user_id].add_job(job)
        self.currently_running_jobs.remove(job)
        self.cpu_snapshot.archive_old_slices(current_time)
        self.cpu_snapshot.delTailofJobFromCpuSlices(job)
        return [
            JobStartEvent(current_time, job)
            for job in self._schedule_jobs(current_time)
        ]


    def _schedule_jobs(self, current_time):
        "Schedules jobs that can run right now, and returns them"
        jobs  = self._schedule_head_of_list(current_time)
        jobs += self._backfill_jobs(current_time)
        return jobs


    def _schedule_head_of_list(self, current_time):     
        result = []
        while True:
            if len(self.unscheduled_jobs) == 0:
                break
            # Try to schedule the first job
            if self.cpu_snapshot.free_processors_available_at(current_time) >= self.unscheduled_jobs[0].num_required_processors:
                job = self.unscheduled_jobs.pop(0)
                self.currently_running_jobs.append(job)
                self.cpu_snapshot.assignJob(job, current_time)
                result.append(job)
            else:
                # first job can't be scheduled
                break
        return result
    

    def _backfill_jobs(self, current_time):
        if len(self.unscheduled_jobs) <= 1:
            return []

        result    = []  
        first_job = self.unscheduled_jobs[0]        
        tail      = list_copy(self.unscheduled_jobs[1:]) 
                
        for job in tail:
            if self.can_be_probabilistically_backfilled(job, current_time):
                self.unscheduled_jobs.remove(job)
                self.currently_running_jobs.append(job)
                self.cpu_snapshot.assignJob(job, current_time)
                result.append(job)                
        return result


    def can_be_probabilistically_backfilled(self, job, current_time):
        assert len(self.unscheduled_jobs) >= 2
        assert job in self.unscheduled_jobs[1:]

        if self.cpu_snapshot.free_processors_available_at(current_time) < job.num_required_processors:
            return False

        first_job = self.unscheduled_jobs[0]

        prediction  = 0.0
        max_bottle_neck = 0.0 
        bottle_neck = 0.0 
        t = 1

        while t < 2 * job.user_estimated_run_time:
            job_probability_to_end_at_t = self.probability_to_end_at(t, job)
            max_bottle_neck = max(max_bottle_neck, self.bottle_neck(t, job, first_job, current_time))
            prediction += job_probability_to_end_at_t * max_bottle_neck
            t = t * 2 
    
        if prediction <= self.threshold:
            return True
         
        return False
        

    def bottle_neck(self, time, second_job, first_job, current_time):
        C = first_job.num_required_processors + second_job.num_required_processors
        K = min(self.num_processors, C)

        # M[n,c] is the probability that the first n running jobs will release at least c processors at _time_
        M = self.M

        num_of_currently_running_jobs = len(self.currently_running_jobs)
        
        for c in xrange(K + 1): 
            M[0, c] = 0.0
            
        for n in xrange(1, num_of_currently_running_jobs+1):
            M[n, 0] = 1.0

        for n in xrange(1, num_of_currently_running_jobs+1):
            job_n = self.currently_running_jobs[n-1] # the n'th job: recall that a list has a zero index   
            job_n_required_processors = job_n.num_required_processors
            Pn = self.probability_of_running_job_to_end_upto(time, current_time, job_n)
            for c in xrange (1, job_n_required_processors):
                val = M[n-1, c]
                M[n, c] = val + (1.0 - val) * Pn
            for c in xrange (job_n_required_processors, K + 1):
                val = M[n-1, c]
                M[n, c] = val + (M[n, c - job_n_required_processors] - val) * Pn

        last_row_index = num_of_currently_running_jobs
        if  C <= K:  
            result = M[last_row_index, first_job.num_required_processors] - M[last_row_index, C]
        else:   
            result = M[last_row_index, first_job.num_required_processors]

        if   result < 0:
            result = 0.0
        elif result > 1:
            reuslt = 1.0
            
        assert 0 <= result <= 1 
        return result 


    def probability_of_running_job_to_end_upto(self, time, current_time, job):

        run_time = current_time - job.start_to_run_at_time
        rounded_down_run_time = _round_time_down(run_time)
        rounded_up_estimated_remaining_duration = _round_time_up(job.user_estimated_run_time - rounded_down_run_time)
        if time >= rounded_up_estimated_remaining_duration:
            return 1.0 
    
        
        num_of_jobs_in_first_bins  = 0
        num_of_jobs_in_middle_bins = 0.0
        num_of_jobs_in_last_bins   = 0
        job_distribution = self.user_distribution[job.user_id]

        for (key,value) in job_distribution.bins.iteritems():

            if   key > rounded_up_estimated_remaining_duration:
                num_of_jobs_in_last_bins  += value
                
            elif key <= rounded_down_run_time:
                num_of_jobs_in_first_bins += value

            elif key <= time + rounded_down_run_time:
                num_of_jobs_in_middle_bins += value

            elif time + rounded_down_run_time > key/2 : 
                num_of_jobs_in_middle_bins += float(value*(time+rounded_down_run_time-(key/2))) / (key/2) 

            # at the tail of the middle bin, it won't terminate because of conditional probability
            #else: pass
          
        num_of_irrelevant_jobs = num_of_jobs_in_first_bins + num_of_jobs_in_last_bins
        num_of_relevant_jobs = job_distribution.number_of_jobs_added - num_of_irrelevant_jobs

	assert 0 <= num_of_jobs_in_middle_bins <= num_of_relevant_jobs, \
               str(num_of_jobs_in_middle_bins)+str(" ")+str(num_of_relevant_jobs)

        result = num_of_jobs_in_middle_bins / (num_of_relevant_jobs + 0.1)

        return result 


    def probability_to_end_at(self, time, job):         
        job_distribution = self.user_distribution[job.user_id]
        assert job_distribution.bins.has_key(time) == True
	        
        num_of_jobs_in_last_bins = 0
        rounded_up_user_estimated_run_time = 2 * job.user_estimated_run_time - 1

        for key in job_distribution.bins.keys():  
            if key > rounded_up_user_estimated_run_time:
                num_of_jobs_in_last_bins  += job_distribution.bins[key]  
 
        num_of_relevant_jobs = job_distribution.number_of_jobs_added - num_of_jobs_in_last_bins

	assert 0 <= job_distribution.bins[time] <= num_of_relevant_jobs,\
               str(time)+str(" ")+ str(job_distribution.bins[time])+str(" ")+str(num_of_relevant_jobs)

       	result = float(job_distribution.bins[time]) / (num_of_relevant_jobs + 0.1) 

        return result 
     
     

     
