from predictor import Predictor
import numpy as np
from valopt.models.linear_model import LinearModel
from valopt.algos.nag import NAG

class PredictorSGDLinear(Predictor):
    #Internal info
    n_features=2

    def __init__(self, options):
        #Data structures for storing info
        self.user_job_last3 = {}
        self.user_job_last2 = {}
        self.user_job_last1 = {}
        self.job_x= {}

        #machine learning thing
        m=LinearModel(self.n_features)

        if options["loss"]=="squaredloss":
            from valopt.losses.squared_loss import SquaredLoss
            l=SquaredLoss(m)
        elif options["loss"]=="absloss":
            from valopt.losses.abs_loss import AbsLoss
            l=AbsLoss(m)
        elif options["loss"]=="weightedsquaredloss":
            from valopt.losses.weighted_squared_loss import WeightedSquaredLoss
            l=WeightedSquaredLoss(m)
        else:
            raise ValueError("predictor config error: no valid loss specified.")

        if "max_runtime" in options.keys():
            self.max_runtime=options["max_runtime"]
        else:
            self.max_runtime=False


        self.model=NAG(m,l,options["eta"],verbose=False)


    def make_x(self,job,current_time,list_running_jobs):
        """Make a vector from a job. requires job, current time and system state."""
        x=np.empty(self.n_features,dtype=np.float32)

        #checks on user internal memory
        if not self.user_job_last1.has_key(job.user_id):
            self.user_job_last1[job.user_id] = None
        if not self.user_job_last2.has_key(job.user_id):
            self.user_job_last2[job.user_id] = None
        if not self.user_job_last3.has_key(job.user_id):
            self.user_job_last3[job.user_id] = None

        #TODO:make x
        #x[0] is user estimated run time
        #x[1] is p_i-1, p_i-2 mean

        #Required_time (aka user estimated run time)
        x[0]= job.user_estimated_run_time

        #Moving averages
        if self.user_job_last2[job.user_id] != None:
            #TODO:check if we know already the 2 last run time, take a choice.
            j1= self.user_job_last1[job.user_id]
            j2= self.user_job_last2[job.user_id]
            if j1.submit_time+j1.actual_run_time>current_time:
                last1=j1.actual_run_time
            else:
                last1=current_time-j1.submit_time
            if j2.submit_time+j2.actual_run_time>current_time:
                last2=j2.actual_run_time
            else:
                last2=current_time-j2.submit_time

            average = float((last1+last2)/ 2)
            x[1]    = min(job.user_estimated_run_time, average)
        elif self.user_job_last1[job.user_id] != None:
            #TODO:check if we know already the last run time, take a choice.
            j1= self.user_job_last1[job.user_id]
            if j1.submit_time+j1.actual_run_time>current_time:
                last=j1.actual_run_time
            else:
                last=current_time-j1.submit_time

            x[1]    = min(job.user_estimated_run_time, last)
        else:
            x[1] = job.user_estimated_run_time
        return x

    def store_x(self,job,x):
        """store x for a given job if its not already stored"""
        if job not in self.job_x.keys():
            self.job_x[job]=x

    def pop_x(self, job):
        """retrieve x for a given job and delete it from memory"""
        x=self.job_x.pop(job,[])
        if x==[]:
            raise ValueError("Predictor internal x memory failed.")
        return x

    def predict(self, job, current_time, list_running_jobs):
        """
        Modify the predicted_run_time of a job.
        Called when a job is submitted to the system.
        """
        #make x
        x=self.make_x(job,current_time,list_running_jobs)
        #store x
        self.store_x(job,x)
        #make the prediction
        job.predicted_run_time=abs(self.model.predict(x))
        if not self.max_runtime==False:
            job.predicted_run_time=min(job.predicted_run_time,self.max_runtime)


    def fit(self, job, current_time):
        """
        Add a job to the learning algorithm.
        Called when a job end.
        """
        #pop  x from internal data
        x=self.pop_x(job)

        #updating our data
        #store user previous run time history
        assert self.user_job_last1.has_key(job.user_id) == True
        assert self.user_job_last2.has_key(job.user_id) == True
        assert self.user_job_last3.has_key(job.user_id) == True
        self.user_job_last3[job.user_id] = self.user_job_last2[job.user_id]
        self.user_job_last2[job.user_id] = self.user_job_last1[job.user_id]
        self.user_job_last1[job.user_id] = job

        #fit the model
        self.model.fit(x,job.actual_run_time,p=10*np.log(1+(job.actual_run_time/min(1,job.num_required_processors))))
