#! /usr/bin/env python

import sys

class JobEvent(object):

    global_event_counter = 0
    @classmethod
    def next_counter(cls):
        cls.global_event_counter += 1
        return cls.global_event_counter

    def __init__(self, timestamp, job):
        self.timestamp = timestamp
        self.counter   = JobEvent.next_counter()
        self.job = job

    def __repr__(self):
        return type(self).__name__ + "<timestamp=%(timestamp)s, job=%(job)s>" % vars(self)

    def __cmp__(self, other):
        return cmp(self._cmp_tuple, other._cmp_tuple)

    @property
    def _cmp_tuple(self):
        "Order by timestamp and type order. A global counter tie-breaks."
        return (self.timestamp, self._type_order, self.counter)

    def __eq__(self, other):
        return self._eq_tuple == other._eq_tuple

    @property
    def _eq_tuple(self):
        "equal iff timestamp, job, and type are the same"
        return (self.timestamp, self.job, type(self))

    @property
    def _type_order(self):
        if type(self) in self.EVENTS_ORDER:
            return self.EVENTS_ORDER.index(type(self))
        else:
            return sys.maxint

    EVENTS_ORDER = []

class JobSubmissionEvent(JobEvent): pass
class JobStartEvent(JobEvent): pass
class JobTerminationEvent(JobEvent): pass
class JobPredictionIsOverEvent(JobEvent):pass

# tie break rule order for events occuring at the same time 
JobEvent.EVENTS_ORDER = [JobPredictionIsOverEvent, JobSubmissionEvent, JobTerminationEvent, JobStartEvent]

class Job(object):
    def __init__(self, id, user_estimated_run_time, actual_run_time, num_required_processors, \
            submit_time=0, admin_QoS=0, user_QoS=0, user_id=0): # TODO: are these defaults used?

        assert num_required_processors > 0, "job_id=%s"%id
        assert actual_run_time > 0, "job_id=%s"%id
        assert user_estimated_run_time > 0, "job_id=%s"%id

        self.id = id
        self.user_estimated_run_time = user_estimated_run_time
        self.predicted_run_time = user_estimated_run_time  
        self.actual_run_time = actual_run_time
        self.num_required_processors = num_required_processors
	self.user_id = user_id
        
        # not used by base
        self.submit_time = submit_time # Assumption: submission time is greater than zero
        self.start_to_run_at_time = -1 # TODO: convert to None

        # the next are essentially for the MauiScheduler
        self.admin_QoS  = admin_QoS # the priority given by the system administration
        self.user_QoS   = user_QoS # the priority given by the user
        self.maui_bypass_counter = 0
        self.maui_counter = 0

        # the next is for the look ahead scheduler
        self.backfill_flag = 0

        # the next is for the probabilistic easy scheduler
        self.expected_predicted_run_time = user_estimated_run_time 

        
    @property
    def finish_time(self):
        assert self.start_to_run_at_time != -1
        return self.start_to_run_at_time + self.actual_run_time
    
    @property
    def predicted_finish_time(self):
        assert self.start_to_run_at_time != -1
        return self.start_to_run_at_time + self.predicted_run_time

    def __repr__(self):
        return type(self).__name__ + "<id=%(id)s, user_estimated_run_time=%(user_estimated_run_time)s, actual_run_time=%(actual_run_time)s, required_processors=%(num_required_processors)s, start_to_run_at_time=%(start_to_run_at_time)s, submit_time=%(submit_time)s>" % vars(self)

class StupidScheduler(object):
    "A very simple scheduler - schedules jobs one after the other with no chance of overlap"
    def __init__(self):
        self.next_free_time = None

    def handleSubmissionOfJobEvent(self, job, timestamp):
        # init next_free_time to the first timestamp seen
        if self.next_free_time is None:
            self.next_free_time = timestamp

        result = [JobStartEvent(timestamp=self.next_free_time, job=job)]

        self.next_free_time += job.user_estimated_run_time

        return result

    def handleTerminationOfJobEvent(self, job, timestamp):
        return []

class Machine(object):
    "Represents the actual parallel machine ('cluster')"
    def __init__(self, event_queue):
        self.event_queue = event_queue
        self.event_queue.add_handler(JobStartEvent, self._start_job_handler)
        
    def _start_job_handler(self, event):
        assert type(event) == JobStartEvent
        if event.job.start_to_run_at_time not in (-1, event.timestamp):
            # outdated job start event, ignore
            # TODO: remove the possibility for outdated events
            return
        self._add_job(event.job, event.timestamp)

    def _add_job(self, job, current_timestamp):
        assert job.actual_run_time  <= job.user_estimated_run_time
        
        self.event_queue.add_event(JobTerminationEvent(job=job, timestamp=current_timestamp+job.actual_run_time))
        if job.predicted_run_time < job.actual_run_time:
             self.event_queue.add_event(JobPredictionIsOverEvent(job=job, timestamp=current_timestamp+job.predicted_run_time))
            
            
            
class ValidatingMachine(Machine):
    """
    Represents the actual parallel machine ('cluster'), validating proper
    machine usage
    """
    def __init__(self, num_processors, event_queue):
        super(ValidatingMachine, self).__init__(event_queue)
        self.num_processors = num_processors
        self.jobs = set()

        self.event_queue.add_handler(JobTerminationEvent, self._remove_job_handler)

    def _add_job(self, job, current_timestamp):
        assert job.num_required_processors <= self.free_processors
        self.jobs.add(job)
        super(ValidatingMachine, self)._add_job(job, current_timestamp)

    def _remove_job_handler(self, event):
        assert type(event) == JobTerminationEvent
        self.jobs.remove(event.job)

    @property
    def free_processors(self):
        return self.num_processors - self.busy_processors

    @property
    def busy_processors(self):
        return sum(job.num_required_processors for job in self.jobs)

def parse_job_lines_quick_and_dirty(lines):
    """
    parses lines in Standard Workload Format, yielding pairs of (submit_time, <Job instance>)

    This should have been:

      for job_input in workload_parser.parse_lines(lines):
        yield job_input.submit_time, _job_input_to_job(job_input)

    But instead everything is hard-coded (also hard to read and modify) for
    performance reasons.

    Pay special attention to the indices and see that you're using what you
    expect, check out the workload_parser.JobInput properties and
    _job_input_to_job comments to see extra logic that isn't represented here.
    """
    for line in lines:
        x = line.split()
        yield int(x[1]), Job(
            id = int(x[0]),
            user_estimated_run_time = int(x[8]),
            actual_run_time = int(x[3]),
            num_required_processors = max(int(x[7]), int(x[4])), # max(num_requested,max_allocated)
        )

def _job_input_to_job(job_input, total_num_processors):
    # if job input seems to be problematic  
    if job_input.run_time <= 0 or job_input.num_allocated_processors <= 0 or job_input.submit_time < 0 :
        return Job(
            id = job_input.number,
            user_estimated_run_time = 1,
            actual_run_time = 1, 
            num_required_processors = max(1, job_input.num_allocated_processors),  
            submit_time = max(job_input.submit_time, 1), 
            user_id = job_input.user_id, 
        )

    return Job(
        id = job_input.number,
        user_estimated_run_time = int(max(job_input.requested_time, job_input.run_time, 1)),
        actual_run_time = int(max(min(job_input.requested_time, job_input.run_time), 1)), 
        num_required_processors = max(min(job_input.num_allocated_processors, total_num_processors), 1), 
        submit_time = job_input.submit_time, 
        user_id = job_input.user_id, 
    )

def _job_inputs_to_jobs(job_inputs, total_num_processors):
    for job_input in job_inputs:
        yield _job_input_to_job(job_input, total_num_processors)

from event_queue import EventQueue
class Simulator(object):
    def __init__(self, jobs, num_processors, scheduler):
        self.event_queue = EventQueue()
        self.machine = ValidatingMachine(num_processors=num_processors, event_queue=self.event_queue)
        self.scheduler = scheduler

        self.event_queue.add_handler(JobSubmissionEvent, self.handle_submission_event)
        self.event_queue.add_handler(JobTerminationEvent, self.handle_termination_event)

        for job in jobs:
            self.event_queue.add_event(
                    JobSubmissionEvent(timestamp = job.submit_time, job = job)
                )

    def run(self):
        while not self.event_queue.is_empty:
            self.event_queue.advance()

    def handle_submission_event(self, event):
        assert isinstance(event, JobSubmissionEvent)
        newEvents = self.scheduler.handleSubmissionOfJobEvent(event.job, event.timestamp)
        for event in newEvents:
            self.event_queue.add_event(event)

    def handle_termination_event(self, event):
        assert isinstance(event, JobTerminationEvent)
        newEvents = self.scheduler.handleTerminationOfJobEvent(event.job, event.timestamp)
        for event in newEvents:
            self.event_queue.add_event(event)
            
    def handle_prediction_is_over_event(self, event):
        assert isinstance(event, JobPredictionIsOverEvent)
        newEvents = self.scheduler.handlePredictionIsOverEvent(event.job, event.timestamp)
        for event in newEvents:
            self.event_queue.add_event(event)


def simple_job_generator(num_jobs):
    import random
    start_time = 0
    for id in xrange(num_jobs):
        start_time += random.randrange(0, 15)
        yield start_time, Job(
            id=id,
            user_estimated_run_time=random.randrange(400, 2000),
            actual_run_time=random.randrange(30, 1000),
            num_required_processors=random.randrange(2,100),
        )
