import simpy.util


class MonitorCallbackWrapped:
    '''
    Two features:
    1/Callback class with a decorator to call two fonctions, before and after.
    With simpy, I find this useful. You can use it to extend the functionality
    of a class at runtime, as opposed to writing a variant of such class.
    For instance, if you want to perform an operation everytime a job end,
    just add_callbacks_after to every job.
    2/Builtin monitor management. Just set_monitor before starting the simulation
    and call self.run_monitor whenever you want to collect data.
    Here is how to use it:
    -inherit this class
    -add MonitorCallbackWrapped.__init__(self) to constructor 
    -add @callbacked to a fonction that your want to enable the callbacks on.
    -call add_callback_<before/after> to add callbacks
    -call set_monitor to set a simpy monitor
    -call run_monitor to run a round of monitor collecting.
    '''
    def __init__(self,logfunc,description):
        self.log=lambda msg:logfunc('%s '%description+msg)
        self.description=description
        self.callback_before=[]
        self.callback_after=[]
        self.monitored=False


    def clean_callbacks(self):
        self.callback_before=[]
        self.callback_after=[]

    def add_callbacks_before(self,callbacks):
        try:
            self.callback_before.extend(callbacks)
        except TypeError:
            self.callback_before.append(callbacks)

    def add_callbacks_after(self,callbacks):
        try:
            self.callback_after.extend(callbacks)
        except TypeError:
            self.callback_after.append(callbacks)

    def set_monitor(self,monitor):
        self.monitored=True
        self.monitor=monitor

    def run_monitor(self):
        if self.monitored:
            self.monitor.collect()


class System(MonitorCallbackWrapped):
    def __init__(self,env,vschedule,localalgo,hardware,cores,logfunc,sorter):
        self.logfunc=logfunc
        self.env=env
        self.vschedule=vschedule
        self.cores=cores
        self.localalgo=localalgo
        self.hardware=hardware
        self.sorter=sorter
        self.vqueue=[]
        MonitorCallbackWrapped.__init__(self,logfunc,'SYSTEM')

    def start(self):
        self.log('starting system components..' )
        self.log('the system has %s cores'%self.cores )
        self.hardware.start()
        self.vschedule.start(self,self.hardware)
        self.log('all system components started.' )
        self.log('starting simulation.' )

    def stop(self):
        self.vschedule.stop()
        self.hardware.stop()

    def submit(self,campaign):
        self.log('campaign submission: %s.' %campaign)
        self.vschedule.submit(campaign)

    def update_virtual_queue(self,new_vqueue):
        #self.log('recieving an incoming queue from the virtual schedule.: %s'%new_vqueue )
        #self.log('previous system queue: %s'%self.vqueue)
        q=[]
        for c in self.vqueue:
            if c not in new_vqueue:
                q.append(c)
        q.extend(new_vqueue)
        self.log('debug1')
        new=False
        if len(self.vqueue)==len(q):
            for i in range(0,len(q)):
                if not q[i]==self.vqueue[i]:
                    new=True
        else:
            new=True
        self.vqueue=q
        self.run_monitor
        if new:
            orders=self.localalgo(self.env,self.hardware.get_status(),self.vqueue,self.cores,self.sorter,self.logfunc)
            self.hardware.submit(orders)

class User(MonitorCallbackWrapped):
    def __init__(self,env,uid,campaign_deque,system,logfunc):
        self.system=system
        self.env=env
        self.uid=uid
        self.campaign_deque=campaign_deque
        self.old_campaigns=[]
        self.over=env.event()
        MonitorCallbackWrapped.__init__(self,logfunc,'USER %s '%self.uid)

    def start(self,f):
        self.f=f
        self.env.start(self.run())

    def run(self):
        while not len(self.campaign_deque)==0:
            campaign=self.campaign_deque.popleft()
            for j in campaign.jobs:
                j.setfile(self.f)
            if campaign.thinktime==0:
                self.log('no thinktime' )
            else:
                self.log('entering thinktime, value %s' %campaign.thinktime)
            yield self.env.timeout(campaign.thinktime)
            self.log('submitting campaign: %s' %campaign)
            yield campaign.start(self.system)
            self.old_campaigns.append(campaign)
            self.run_monitor()
        self.log('all campaigns finished.')
        self.over.succeed()

class Campaign(MonitorCallbackWrapped):
    def __init__(self,env,uid,cid,thinktime, job_list,logfunc):
        self.uid=uid
        self.cid=cid
        self.env=env
        self.thinktime=thinktime
        self.jobs=job_list
        self.workload=sum([j.cores*j.walltime for j in job_list])
        MonitorCallbackWrapped.__init__(self,logfunc,'CAMPAIGN %s '%self.cid)

    def start(self,system):
        self.system=system
        return(self.env.start(self.run()))

    def run(self):
        for f in self.callback_before:
            f(self)
        for j in self.jobs:
            j.submitted()
        self.system.submit(self)
        self.log('waiting for all job ends')
        yield simpy.util.all_of([j.over for j in self.jobs])
        for f in self.callback_after:
            f(self)

    def __repr__(self):
        return('{user %s, cid %s, workload %s, tt %s, %s jobs}'
                %(self.uid,self.cid,self.workload,self.thinktime,len(self.jobs)))

class Job(MonitorCallbackWrapped):
    def __init__(self,env,uid,job_id,cores,reqtime,walltime,logfunc):
        self.env=env
        self.uid=uid
        self.job_id=job_id
        self.cores=cores
        self.reqtime=reqtime
        self.walltime=walltime
        self.over=env.event()
        self.swf_start=0
        self.swf_end=0
        self.swf_subtime=0
        self.started=False
        MonitorCallbackWrapped.__init__(self,logfunc,'')
        


    def setfile(self,f):
        self.f=f

    def get_remaining_walltime(self):
        if self.started and not self.over.triggered:
            return(self.walltime-(self.env.now-self.swf_start))
        elif self.over.triggered:
            return(0)
        else:
            return(self.walltime)

    def submitted(self):
        self.swf_subtime=self.env.now

    def start(self):
        if not self.started:
            self.started=True
            self.log('S %s' %(self))
            self.process=self.env.start(self.run())

    def run(self):
        for f in self.callback_before:
            f(self)
        self.swf_start=self.env.now
        yield self.env.timeout(self.walltime)
        self.log('E %s'%self)
        self.swf_end=self.env.now
        self.over.succeed()
        self.f.write(self.swfstring()+'\n')
        for f in self.callback_after:
            f(self)
            self.log("length of callback after queue: %s" %len(self.callback_after))

    def __repr__(self):
        return('{user %s, id %s, walltime %s, cores %s}'
                %(self.uid,self.job_id,self.walltime,self.cores))

    def swfstring(self):
        return(' %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s'
                %(self.job_id, self.swf_subtime, self.swf_start-self.swf_subtime,
            self.swf_end-self.swf_start, self.cores, -1, -1, self.cores, self.reqtime,
            -1, 1, self.uid, 1, 1, 1, 1, -1, -1)
            )
