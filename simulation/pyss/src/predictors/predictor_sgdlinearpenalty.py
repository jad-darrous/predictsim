from predictor import Predictor
import numpy as np

class PredictorSGDLinear(Predictor):
    n_features=2

    def __init__(self,max_procs=None, max_runtime=None, loss="squared_loss", eta=0.01, regularization="l1",alpha=1,beta=0,verbose=True):
        self.user_run_time_prev = {}
        self.user_run_time_last = {}
        if loss=="squared_loss":
            self.dloss=self.d_squared_loss
        else:
            raise ValueError("only squared_loss is supported")
        assert isinstance(eta,int) or isinstance(eta,float)
        self.eta=eta
        if verbose==True:
            def verb(s):
                print(s)
        else:
            def verb(s):
                pass
        self.w=np.zeros(self.n_features,dtype=np.float32)

    def d_squared_loss(self, p, y):
        return p - y

    def make_x(self,job):
        x=np.empty(self.n_features,dtype=np.float32)

        #Tsafir SMA(2)
        if not self.user_run_time_last.has_key(job.user_id):
            self.user_run_time_prev[job.user_id] = None
            self.user_run_time_last[job.user_id] = None
        if self.user_run_time_prev[job.user_id] != None:
            average = float((self.user_run_time_last[job.user_id] + self.user_run_time_prev[job.user_id])/ 2)
            x[0]    = min(job.user_estimated_run_time, average)
        else:
            x[0] = job.user_estimated_run_time

        #Required_time (aka user estimated run time)
        x[1]= job.user_estimated_run_time
        return x

    def apply_model(self,x):
        return np.dot(self.w,x)

    def predict(self, job, current_time):
        x                      = self.make_x(job)
        job.predicted_run_time = self.apply_model(x)

    def update_model(self,job):
        x     = self.make_x(job)
        p     = self.apply_model(x)
        y     = job.actual_run_time
        dloss = self.dloss(p,y)
        self.w     = self.w-self.eta*np.dot(dloss,x)
        verb(np.mean(w))
        verb(max(w))

    def fit(self, job, current_time):
        self.update_model(job)

        #History for Tsafir SMA(2)
        assert self.user_run_time_last.has_key(job.user_id) == True
        assert self.user_run_time_prev.has_key(job.user_id) == True
        self.user_run_time_prev[job.user_id] = self.user_run_time_last[job.user_id]
        self.user_run_time_last[job.user_id] = job.actual_run_time
