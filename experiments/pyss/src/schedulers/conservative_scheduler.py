from common import Scheduler, CpuSnapshot
from base.prototype import JobStartEvent

class ConservativeScheduler(Scheduler):

    def __init__(self, num_processors):
        super(ConservativeScheduler, self).__init__(num_processors)
        self.cpu_snapshot = CpuSnapshot(num_processors)
        self.unfinished_jobs_by_submit_time = []

    def new_events_on_job_submission(self, job, current_time):
        self.cpu_snapshot.archive_old_slices(current_time)
        self.unfinished_jobs_by_submit_time.append(job)
        self.cpu_snapshot.assignJobEarliest(job, current_time)
        return [ JobStartEvent(job.start_to_run_at_time, job) ]

    def new_events_on_job_termination(self, job, current_time):
        """ Here we delete the tail of job if it was ended before the duration declaration.
        It then reschedules the remaining jobs and returns a collection of new termination events
        (using the dictionary data structure) """
        self.cpu_snapshot.archive_old_slices(current_time)
        self.unfinished_jobs_by_submit_time.remove(job)
        self.cpu_snapshot.delTailofJobFromCpuSlices(job)
        return self._reschedule_jobs(current_time)

    def _reschedule_jobs(self, current_time):
        newEvents = []
        for job in self.unfinished_jobs_by_submit_time:
            if job.start_to_run_at_time <= current_time:
                continue # job started to run before, so it cannot be rescheduled (preemptions are not allowed)
            prev_start_to_run_at_time = job.start_to_run_at_time
            self.cpu_snapshot.delJobFromCpuSlices(job)
            self.cpu_snapshot.assignJobEarliest(job, current_time)
            assert prev_start_to_run_at_time >= job.start_to_run_at_time
            if prev_start_to_run_at_time != job.start_to_run_at_time:
                newEvents.append( JobStartEvent(job.start_to_run_at_time, job) )
        return newEvents
