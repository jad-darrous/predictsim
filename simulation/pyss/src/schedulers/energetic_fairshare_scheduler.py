from common import CpuSnapshot



from easy_backfill_scheduler import EasyBackfillScheduler

class EnergeticFairshareScheduler(EasyBackfillScheduler):
    def __init__(self, options):
        super(EnergeticFairshareScheduler, self).__init__(options)
        
        user_cputime_counter = {}
        user_energy_counter = {}
        
        take_into_account_cputime = True
        take_into_account_energy = True
        

    def new_events_on_job_submission(self, just_submitted_job, current_time):
        "Overriding parent method"
        return super(EnergeticFairshareScheduler, self).new_events_on_job_submission(just_submitted_job, current_time)


    def _schedule_jobs(self, current_time):
        "Overriding parent method"
        self.unscheduled_jobs.sort(
                key = lambda x: self.waiting_list_weight(x, current_time),
                reverse=True
            )

        return super(EnergeticFairshareScheduler, self)._schedule_jobs(current_time)



    def waiting_list_weight(self, job, current_time):
        wait = current_time - job.submit_time # wait time since submission of job
        sld = (wait + job.user_estimated_run_time) /  job.user_estimated_run_time

        return (
            weights.wtime  * wait +
            weights.sld    * sld +
            weights.user   * job.user_QoS +
            weights.bypass * job.maui_bypass_counter +
            weights.admin  * job.admin_QoS +
            weights.size   * job.num_required_processors
        )

