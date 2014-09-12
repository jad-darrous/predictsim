from predictor import Predictor
import numpy as np
import itertools
from scipy.special import binom
from valopt.models.linear_model import LinearModel
from valopt.algos.nag import NAG

class PredictorSgdlinear(Predictor):
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

        #Statistics oriented.
        self.last_loss=0

        if options["quadratic"]:
            self.quadratic=True
            self.n_features=int(self.n_features+binom(self.n_features,2))

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
        elif options["loss"]=="asymetricweightedsquaredloss":
            from valopt.losses.asymetric_weighted_squared_loss import AsymetricWeightedSquaredLoss
            if not options["beta"]:
                raise ValueError("predictor config error: no valid beta value for asymetric loss specified.")
            if not options["gamma"]:
                raise ValueError("predictor config error: no valid gamma value for asymetric loss specified.")
            l=AsymetricWeightedSquaredLoss(m,options['beta'],options["gamma"])
        else:
            raise ValueError("predictor config error: no valid loss specified.")

        if "max_runtime" in options.keys():
            self.max_runtime=options["max_runtime"]
        else:
            self.max_runtime=False

        self.model=NAG(m,l,options["eta"],verbose=False)

        if not options["weight"]:
            wstr="1"
        else:
            wstr=options["weight"]

        def weight(job):
            m=float(job.num_required_processors)
            r=float(job.actual_run_time)
            log=np.log
            return eval(wstr)
        self.weight=weight


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

        if not self.user_sum_cores.has_key(job.user_id):
            self.user_sum_cores[job.user_id] = 0
        if not self.user_sum_runtimes.has_key(job.user_id):
            self.user_sum_runtimes[job.user_id] = 0
        if not self.user_n_jobs.has_key(job.user_id):
            self.user_n_jobs[job.user_id] = 0
        if not self.user_last_ending.has_key(job.user_id):
            self.user_last_ending[job.user_id] = 0

        #TODO:make x
        #x[0] is 1
        #x[1] is last user run time
        #x[2] is last user run time2
        #x[3] is last user run time3
        #x[4] is user request
        #x[5] is moving average(3)
        #x[6] is moving average(2)
        #x[7] is user runtime mean
        #x[8] is time since last time a job of the user ended.

        #Turning linear model into affine model
        x[0]=1

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

        #second of day
        #x[14]=current_time % 3600*60
        #cos second of day
        x[14]=np.cos(3600*60*2*np.pi*x[14])
        #sin second of day
        x[15]=np.sin(3600*60*2*np.pi*x[14])
        #day of week trough seconds:
        #x[14]=current_time % 3600*60*7
        #cos day of week
        x[16]=np.cos(7*3600*60*2*np.pi*x[14])
        #sin day of week
        x[17]=np.sin(7*3600*60*2*np.pi*x[14])

        if self.quadratic:
            i=1
            for a,b in itertools.combinations(x[0:18],2):
                x[17+i]=a*b
                i+=1

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
        job.predicted_run_time=abs(self.model.predict(x))
        if not self.max_runtime==False:
            job.predicted_run_time=min(job.predicted_run_time,self.max_runtime)

        return self.model.loss.loss(x,job.actual_run_time,self.weight(job))


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
        self.model.fit(x,job.actual_run_time,w=self.weight(job))
