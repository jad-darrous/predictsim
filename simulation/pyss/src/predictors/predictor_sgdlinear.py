from predictor import Predictor
import numpy as np

class PredictorSGDLinear(Predictor):
    n_features=2

    def __init__(self,max_procs=None, max_runtime=None,verbose=True):
        self.user_run_time_last3 = {}
        self.user_run_time_last2 = {}
        self.user_run_time_last1 = {}


    #def make_x(self,job):
        #x=np.empty(self.n_features,dtype=np.float32)

        ##Tsafir SMA(2)
        #if not self.user_run_time_last.has_key(job.user_id):
            #self.user_run_time_last1[job.user_id] = None
            #self.user_run_time_last2[job.user_id] = None
            #self.user_run_time_last3[job.user_id] = None
        #if self.user_run_time_prev[job.user_id] != None:
            #average = float((self.user_run_time_last[job.user_id] + self.user_run_time_prev[job.user_id])/ 2)
            #x[0]    = min(job.user_estimated_run_time, average)
        #else:
            #x[0] = job.user_estimated_run_time

        ##Required_time (aka user estimated run time)
        #x[1]= job.user_estimated_run_time
        #return x

    def predict(self, job, current_time):
        if not self.user_run_time_last.has_key(job.user_id):
            self.user_run_time_last1[job.user_id] = None
            self.user_run_time_last2[job.user_id] = None
            self.user_run_time_last3[job.user_id] = None

    def fit(self, job, current_time):
        #run time history
        assert self.user_run_time_last1.has_key(job.user_id) == True
        assert self.user_run_time_last2.has_key(job.user_id) == True
        assert self.user_run_time_last3.has_key(job.user_id) == True
        self.user_run_time_last3[job.user_id] = self.user_run_time_last2[job.user_id]
        self.user_run_time_last2[job.user_id] = self.user_run_time_last1[job.user_id]
        self.user_run_time_last1[job.user_id] = job.actual_run_time
