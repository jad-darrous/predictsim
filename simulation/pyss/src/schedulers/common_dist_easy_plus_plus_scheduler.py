from easy_plus_plus_scheduler import EasyPlusPlusScheduler

    
class  CommonDistEasyPlusPlusScheduler(EasyPlusPlusScheduler):
    """ This algorithm implements a version of Tsafrir, Etsion and Feitelson
        In this version we have a single common distribution for all the jobs and users 
    """
    def new_events_on_job_submission(self, job, current_time):
        # TODO: Ugly patch - making all jobs have the same user id 
        # Warning - loses the original user_id, don't use the same jobs with other schedulers after
        job.user_id = "common_dist"
        return super(CommonDistEasyPlusPlusScheduler, self).new_events_on_job_submission(job, current_time)
