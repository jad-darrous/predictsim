from common import Scheduler, CpuSnapshot, list_copy 
from base.prototype import JobStartEvent

class EasyBackfillScheduler(Scheduler):

    def __init__(self, num_processors):
        super(EasyBackfillScheduler, self).__init__(num_processors)
        self.cpu_snapshot = CpuSnapshot(num_processors)
        self.unscheduled_jobs = []

    def new_events_on_job_submission(self, just_submitted_job, current_time):
        """ Here we first add the new job to the waiting list. We then try to schedule
        the jobs in the waiting list, returning a collection of new termination events """
        # TODO: a probable performance bottleneck because we reschedule all the
        # jobs. Knowing that only one new job is added allows more efficient
        # scheduling here.
        self.cpu_snapshot.archive_old_slices(current_time)
        self.unscheduled_jobs.append(just_submitted_job)
        return [
            JobStartEvent(current_time, job)
            for job in self._schedule_jobs(current_time)
        ]

    def new_events_on_job_termination(self, job, current_time):
        """ Here we first delete the tail of the just terminated job (in case it's
        done before user estimation time). We then try to schedule the jobs in the waiting list,
        returning a collection of new termination events """
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
                self.cpu_snapshot.assignJob(job, current_time)
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
                result.append(job)

        return result 

    def canBeBackfilled(self, second_job, current_time):
        assert len(self.unscheduled_jobs) >= 2
        assert second_job in self.unscheduled_jobs[1:]

        if self.cpu_snapshot.free_processors_available_at(current_time) < second_job.num_required_processors:
            return False

        first_job = self.unscheduled_jobs[0]

        temp_cpu_snapshot = self.cpu_snapshot.copy()
        temp_cpu_snapshot.assignJobEarliest(first_job, current_time)

        # if true, this means that the 2nd job is "independent" of the 1st, and thus can be backfilled
        return temp_cpu_snapshot.canJobStartNow(second_job, current_time)


   
