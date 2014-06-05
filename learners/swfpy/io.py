import unicodecsv
from collections import namedtuple
from StringIO import StringIO
import numpy as np

def swfopen(filename,output="ntuplearray"):
    """open the filename and return \'tuplearray\' or \'np.array\'"""
    if output=='ntuplearray':
        f = open(filename, 'rt')
        r = unicodecsv.reader(f, encoding='utf-8')
        Job= namedtuple('Job','job_id submit_time wait_time run_time proc_alloc cpu_time_used mem_used proc_req time_req mem_req status user_id group_id exec_id queue_id partition_id previous_job_id think_time')
        data=[]
        for row in r:
            data.append(Job(*map(eval,row[0].split())))
        f.close()
        return data
    elif output=="np.array":
        with open (filename, "r") as f:
            #d=f.read()
            #print StringIO(d)
            data=np.loadtxt(f, dtype={'names': ('job_id',' submit_time',' wait_time',' run_time',' proc_alloc',' cpu_time_used',' mem_used',' proc_req',' time_req',' mem_req',' status',' user_id',' group_id',' exec_id',' queue_id',' partition_id',' previous_job_id',' think_time'),
                'formats':(np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32,np.int32)})
            return data
        #data = np.recfromcsv(filename,delimiter=None)
        #return data


