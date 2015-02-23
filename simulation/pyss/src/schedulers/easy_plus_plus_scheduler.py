from common import Scheduler, CpuSnapshot, list_copy
from base.prototype import JobStartEvent


# shortest job first
sjf_sort_key = (
    lambda job :  job.predicted_run_time
)


class  EasyPlusPlusScheduler(Scheduler):
    """ This algorithm implements the algorithm in the paper of Tsafrir, Etzion, Feitelson, june 2007?
    """

    I_NEED_A_PREDICTOR = True

    def __init__(self, options):
        super(EasyPlusPlusScheduler, self).__init__(options)
        self.init_predictor(options)
        self.init_corrector(options)

        self.cpu_snapshot = CpuSnapshot(self.num_processors, options["stats"])
        self.unscheduled_jobs = []


    def new_events_on_job_submission(self, job, current_time):

        self.cpu_snapshot.archive_old_slices(current_time)
        self.unscheduled_jobs.append(job)
        return [
            JobStartEvent(current_time, job)
            for job in self._schedule_jobs(current_time)
        ]


    def new_events_on_job_termination(self, job, current_time):
        self.predictor.fit(job, current_time)

        if self.corrector.__name__=="ninetynine":
            self.pestimator.fit(job.actual_run_time/job.user_estimated_run_time)

        self.cpu_snapshot.archive_old_slices(current_time)
        self.cpu_snapshot.delTailofJobFromCpuSlices(job)
        return [
            JobStartEvent(current_time, job)
            for job in self._schedule_jobs(current_time)
        ]


    def new_events_on_job_under_prediction(self, job, current_time):
        assert job.predicted_run_time <= job.user_estimated_run_time

        if not hasattr(job,"num_underpredict"):
            job.num_underpredict = 0
        else:
            job.num_underpredict += 1

        if self.corrector.__name__=="ninetynine":
            new_predicted_run_time = self.corrector(self.pestimator,job,current_time)
        else:
            new_predicted_run_time = self.corrector(job, current_time)

        #set the new predicted runtime
        self.cpu_snapshot.assignTailofJobToTheCpuSlices(job, new_predicted_run_time)
        job.predicted_run_time = new_predicted_run_time

        return [JobStartEvent(current_time, job)]


    def _schedule_jobs(self, current_time):
        "Schedules jobs that can run right now, and returns them"

        for job in self.unscheduled_jobs:
            self.predictor.predict(job, current_time, self.running_jobs)
            if not hasattr(job,"initial_prediction"):
                job.initial_prediction=job.predicted_run_time

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
        if len(self.unscheduled_jobs) <= 1:
            return []

        result = []
        first_job = self.unscheduled_jobs[0]
        tail =  list_copy(self.unscheduled_jobs[1:])
        tail_of_jobs_by_sjf_order = sorted(tail, key=sjf_sort_key)

        self.cpu_snapshot.assignJobEarliest(first_job, current_time)

        for job in tail_of_jobs_by_sjf_order:
            if self.cpu_snapshot.canJobStartNow(job, current_time):
                job.is_backfilled = 1
                self.unscheduled_jobs.remove(job)
                self.cpu_snapshot.assignJob(job, current_time)
                result.append(job)

        self.cpu_snapshot.delJobFromCpuSlices(first_job)

        return result

