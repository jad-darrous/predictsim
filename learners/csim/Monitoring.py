from simpy.monitoring import Backend,Monitor
from progressbar import *
'''
The sympy monitor classes for this project.
'''

class FileBackend(Backend):
    ''' prints all appended strings to a log file,
    adding the simpy date, and
    flushing the buffer on the fly.
    '''
    def __init__(self,env,filename='out.log'):
        self.f=open(filename,'w+')
        self.env=env
    def append(self, msg):
        prefix=str(self.env.now)
        self.f.write(prefix+': '+msg+'\n')
        self.f.flush()

def user_collector(user):
    def collector():
        l= len(user.campaign_deque)
        return 'user %s has %s campaigns queued.'%(user.uid,l) 
    return collector

def user_monitor(user,env, backend):
    monitor = Monitor()
    monitor.configure(user_collector(user), backend=backend)
    return monitor

def system_collector(system):
    def collector():
        return 'the system has a vqueue of length %s'%len(system.vqueue)
    return collector

def system_monitor(system,env, backend):
    monitor = Monitor()
    monitor.configure(system_collector(system), backend=backend)
    return monitor

class Cronjob:
    def __init__(self,env,delay,f):
        self.env=env
        self.delay=delay
        self.f=f
        self.stopflag=False
    
    def stop(self):
        self.stopflag=True
    
    def start(self):
        return self.env.start(self.run())

    def run(self):
        while not self.stopflag:
            self.f()
            yield self.env.timeout(self.delay)
        self.env.exit()

class Cronjob_progression(Cronjob):
    def __init__(self,env,delay,users,filename):
        Cronjob.__init__(self,env,delay,self.user_summary) 
        self.users=users
        self.totalcampaigns=sum([len(u.campaign_deque) for u in users])
        widgets = [ Percentage(), ' ',
                   Bar(marker='0',left='[',right=']'),
                   ' ', ETA(),' ',Timer()]
        self.pbar= ProgressBar(widgets=widgets, maxval=self.totalcampaigns)

    def user_summary(self):
        campaigncount=sum([len(u.campaign_deque) for u in self.users])
        self.pbar.update(self.totalcampaigns-campaigncount)

    def start(self):
        self.pbar.start()
        Cronjob.start(self)

    def stop(self):
        self.pbar.finish()
        Cronjob.stop(self)
