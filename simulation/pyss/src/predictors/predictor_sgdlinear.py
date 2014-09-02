from predictor import Predictor
import numpy as np
from valopt.models.linear_model import LinearModel
from valopt.losses.squared_loss import SquaredLoss
from valopt.algos.nag import NAG

class PredictorSGDLinear(Predictor):
    #Internal info
    n_features=2

    def __init__(self,config_dict):
        #Data structures for storing info
        self.user_job_last3 = {}
        self.user_job_last2 = {}
        self.user_job_last1 = {}
        self.job_x= {}

        #machine learning thing
        m=LinearModel(2)
        l=SquaredLoss(m)
        alg=NAG(m,l,,verbose=verbose)


    def make_x(self,job,running_jobs):
        """Make a vector from a job. requires job, current time and system state."""
        x=np.empty(self.n_features,dtype=np.float32)

        #checks on user internal memory
        if not self.user_run_time_last.has_key(job.user_id):
            self.user_job_last1[job.user_id] = None
            self.user_job_last2[job.user_id] = None
            self.user_job_last3[job.user_id] = None

        #TODO:make x    
        #if self.user_run_time_prev[job.user_id] != None:
            #average = float((self.user_run_time_last[job.user_id] + self.user_run_time_prev[job.user_id])/ 2)
            #x[0]    = min(job.user_estimated_run_time, average)
        #else:
            #x[0] = job.user_estimated_run_time
        #Required_time (aka user estimated run time)
        #x[1]= job.user_estimated_run_time

        return x

    def store_x(self,job,x):
        """store x for a given job if its not already stored"""
        if not x in self.job_x.keys():
            self.job_x[job]=x

    def pop_x(self, job):
        """retrieve x for a given job and delete it from memory"""
        x=self.job_x.pop(x,False)
        if not x:
            raise ValueError("Predictor internal x memory failed.")
        return x

    def predict(self, job, current_time, system_state):
        """
        Modify the predicted_run_time of a job.
        Called when a job is submitted to the system.
        """
        #make x
        x=make_x(job)
        #store x
        store_x(job,x)
        #make the prediction
        job.predicted_run_time=self.model.predict(x)

    def fit(self, job, current_time):
        """
        Add a job to the learning algorithm.
        Called when a job end.
        """

        #Pop  x from internal data
        x=pop_x(job)

        #Updating our data
        #store user previous run time history
        assert self.user_job_last1.has_key(job.user_id) == True
        assert self.user_job_last2.has_key(job.user_id) == True
        assert self.user_job_last3.has_key(job.user_id) == True
        self.user_job_last3[job.user_id] = self.user_job_last2[job.user_id]
        self.user_job_last2[job.user_id] = self.user_job_last1[job.user_id]
        self.user_job_last1[job.user_id] = job

        #Fit the model
        self.model.fit(x,job.actual_run_time)
