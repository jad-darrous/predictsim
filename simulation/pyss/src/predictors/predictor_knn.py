from predictor import Predictor
#import numpy as np
import math
import itertools
from valopt.models.knn import KNN
from math import sqrt

from operator import mul    # or mul=lambda x,y:x*y
from fractions import Fraction

def kPn(n,k):
  return int( reduce(mul, (Fraction(n-i, i+1) for i in range(k)), 1) )

class PredictorKNN(Predictor):
    #Internal info
    n_features=18

    def __init__(self, options):
        #Data structures for storing info
        self.user_job_last3 = {}
        self.user_job_last2 = {}
        self.user_job_last1 = {}
        self.user_sum_runtimes = {}
        self.user_sum_cores = {}
        self.user_n_jobs = {}
        self.job_x= {}
        self.user_last_ending = {}

        if "max_runtime" in options["scheduler"]["predictor"].keys():
            self.max_runtime=options["scheduler"]["predictor"]["max_runtime"]
        else:
            self.max_runtime=False

        #todo
        if self.max_runtime:
            mrun=self.max_runtime
        else:
            mrun=5000

        dist=lambda x,y:sqrt(
         (x==y)*options["scheduler"]["predictor"]["alpha_uid"]                      +# x[0] is 1
         options["scheduler"]["predictor"]["alpha_mas"]*(0.9/mrun)*(x[1] -y[1] )**2 +# x[1] is last user run time
         options["scheduler"]["predictor"]["alpha_mas"]*(0.9/mrun)*(x[2] -y[2] )**2 +# x[2] is last user run time2
         options["scheduler"]["predictor"]["alpha_mas"]*(0.9/mrun)*(x[3] -y[3] )**2 +# x[3] is last user run time3
         options["scheduler"]["predictor"]["alpha_mas"]*(0.9/mrun)*(x[4] -y[4] )**2 +# x[4] is user request
         options["scheduler"]["predictor"]["alpha_mas"]*(0.9/mrun)*(x[5] -y[5] )**2 +# x[5] is moving average(3)
         options["scheduler"]["predictor"]["alpha_mas"]*(2/mrun)*(x[6] -y[6] )**2   +# x[6] is moving average(2)
         options["scheduler"]["predictor"]["alpha_umean"]*(1/mrun)*(x[7] -y[7] )**2 +# x[7] is user runtime mean
         options["scheduler"]["predictor"]["alpha_think"]*(1/mrun)*(x[8] -y[8] )**2 +# x[8] is time since last time a job of the user ended.
         options["scheduler"]["predictor"]["alpha_cores"]*(x[9] -y[9] )**2          +# x[9] Ratio of Cores from user mean to this one.
         options["scheduler"]["predictor"]["alpha_cores"]*(1/50)*(x[10]-y[10])**2   +#> x10>tota>core running by this user
         options["scheduler"]["predictor"]["alpha_cores"]*(1/mrun)*(x[11]-y[11])**2 +# x[11] sum of runtime of already running jobs of the user
         options["scheduler"]["predictor"]["alpha_cores"]*(x[12]-y[12])**2           +# x[12] amount of jobs  of this user already running
         options["scheduler"]["predictor"]["alpha_cores"]*(1/mrun)*(x[13]-y[13])**2  +# x[13] length of longest job of user already running
         options["scheduler"]["predictor"]["alpha_hod"]*(min(x[14]-y[14],y[14]-x[14])/12)**2  +# x[14] second of day
         options["scheduler"]["predictor"]["alpha_dow"]*(min(x[15]-y[15],y[15]-x[15])/7)**2        # x[15] day of week
        )
        self.model=KNN(dist,lambda y: y,lambda d:1/max(0.05,d),options["scheduler"]["predictor"]["k"])

    def make_x(self,job,current_time,list_running_jobs):
        """Make a vector from a job. requires job, current time and system state."""
        #x=np.empty(self.n_features,dtype=np.float32)
        x=[0]*self.n_features

        #checks on user internal memory
        if not self.user_job_last1.has_key(job.user_id):
            self.user_job_last1[job.user_id] = None
        if not self.user_job_last2.has_key(job.user_id):
            self.user_job_last2[job.user_id] = None
        if not self.user_job_last3.has_key(job.user_id):
            self.user_job_last3[job.user_id] = None

        if not self.user_sum_cores.has_key(job.user_id):
            self.user_sum_cores[job.user_id] = 0
        if not self.user_sum_runtimes.has_key(job.user_id):
            self.user_sum_runtimes[job.user_id] = 0
        if not self.user_n_jobs.has_key(job.user_id):
            self.user_n_jobs[job.user_id] = 0
        if not self.user_last_ending.has_key(job.user_id):
            self.user_last_ending[job.user_id] = 0

        #TODO:make x
        #x[0] is uid
        #x[1] is last user run time
        #x[2] is last user run time2
        #x[3] is last user run time3
        #x[4] is user request
        #x[5] is moving average(3)
        #x[6] is moving average(2)
        #x[7] is user runtime mean
        #x[8] is time since last time a job of the user ended.

        #Turning linear model into affine model
        x[0]=job.user_id

        #Last runtime
        if self.user_job_last1[job.user_id] != None:
            j1= self.user_job_last1[job.user_id]
            if j1.submit_time+j1.actual_run_time>current_time:
                last=j1.actual_run_time
            else:
                last=current_time-j1.submit_time
        else:
            last=job.user_estimated_run_time
        x[1] = min(job.user_estimated_run_time, last)

        #Last runtime2
        if self.user_job_last2[job.user_id] != None:
            j2= self.user_job_last2[job.user_id]
            if j2.submit_time+j2.actual_run_time>current_time:
                last=j2.actual_run_time
            else:
                last=current_time-j2.submit_time
        else:
            last=job.user_estimated_run_time
        x[2] = min(job.user_estimated_run_time, last)

        #Last runtime3
        if self.user_job_last3[job.user_id] != None:
            j3= self.user_job_last3[job.user_id]
            if j3.submit_time+j3.actual_run_time>current_time:
                last=j3.actual_run_time
            else:
                last=current_time-j3.submit_time
        else:
            last=job.user_estimated_run_time
        x[3] = min(job.user_estimated_run_time, last)

        #Required_time (aka user estimated run time)
        x[4]= job.user_estimated_run_time

        #Moving averages
        if self.user_job_last3[job.user_id] != None:
            x[6]=0.33*(x[1]+x[2]+x[3])
            x[5]=0.5*(x[1]+x[2])
        elif self.user_job_last2[job.user_id] != None:
            x[5]=0.5*(x[1]+x[2])
            x[6]=x[5]
        elif self.user_job_last1[job.user_id] != None:
            x[5]=x[1]
            x[6]=x[5]
        else:
            x[5]=job.user_estimated_run_time
            x[6]=x[5]

        #User run time mean
        if not self.user_n_jobs[job.user_id] ==0:
            x[7]=self.user_sum_runtimes[job.user_id]/self.user_n_jobs[job.user_id]
            #print "ifed"
            #print x[7]
        else:
            x[7]=0
            #print "elsed"

        #T since Last job ending of this user
        if not self.user_last_ending[job.user_id]==0:
            x[8]=current_time-self.user_last_ending[job.user_id]
        else:
            x[8]=0

        #Ratio of Cores from user mean to this one.
        #User cores mean
        if not self.user_n_jobs[job.user_id] ==0:
            coremean=float(self.user_sum_cores[job.user_id])/float(self.user_n_jobs[job.user_id])
            x[9]=job.num_required_processors
        else:
            x[9]=0

        running_mine=[j for j in list_running_jobs if j.user_id==job.user_id]

        #total cores running by this user
        x[10]=sum([j.num_required_processors for j in running_mine])

        #sum of runtime of already running jobs of the user
        lengths_running=[current_time-j.submit_time for j in running_mine]
        x[11]=sum(lengths_running)

        #amount of jobs  of this user already running
        x[12]=len(running_mine)

        #length of longest job of user already running
        if len(lengths_running)==0:
            x[13]=0
        else:
            x[13]=max(lengths_running)

        #hour of day
        x[14]=current_time % (3600*60)
        #cos second of day
        #x[14]=math.cos(3600*60*2*math.pi*x[14])
        #sin second of day
        #x[15]=math.sin(3600*60*2*math.pi*x[14])
        #day of week trough seconds:
        x[15]=current_time % (3600*60*7)
        #cos day of week
        #x[16]=math.cos(7*3600*60*2*math.pi*x[14])
        #sin day of week
        #x[17]=math.sin(7*3600*60*2*math.pi*x[14])

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
        if not job in self.job_x.keys():
            #make x
            x=self.make_x(job,current_time,list_running_jobs)
            #store x
            self.store_x(job,x)
        else:
            x=self.job_x[job]

        #make the prediction
        job.predicted_run_time=max(1,int(abs(self.model.predict(x))))
        job.predicted_run_time=min(job.predicted_run_time,job.user_estimated_run_time)
        if not self.max_runtime==False:
            job.predicted_run_time=max(1,min(job.predicted_run_time,self.max_runtime))

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
        assert self.user_sum_runtimes.has_key(job.user_id) == True
        assert self.user_sum_cores.has_key(job.user_id) == True
        assert self.user_n_jobs.has_key(job.user_id) == True
        assert self.user_last_ending.has_key(job.user_id) == True
        self.user_job_last3[job.user_id] = self.user_job_last2[job.user_id]
        self.user_job_last2[job.user_id] = self.user_job_last1[job.user_id]
        self.user_job_last1[job.user_id] = job
        self.user_n_jobs[job.user_id]+=1
        self.user_sum_runtimes[job.user_id]+=job.actual_run_time
        self.user_sum_cores[job.user_id]+=job.num_required_processors
        self.user_last_ending[job.user_id]=current_time

        #fit the model
        self.model.fit(x,job.actual_run_time)
