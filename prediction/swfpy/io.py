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
            if row[0][0]!=';':
                data.append(Job(*map(eval,row[0].split())))
        f.close()
        return data
    elif output=="np.array":
        with open (filename, "r") as f:
            swf_dtype=np.dtype([('job_id',np.int_),('user_id',np.int_),('last_runtime',np.int_),('last_runtime2',np.float32),('last_status',np.int_),('last_status2',np.int_),('thinktime',np.float32),('running_maxlength',np.float32),('running_sumlength',np.float32),('amount_running',np.int_),('running_average_runtime',np.float32),('running_allocatedcores',np.int_)])
            data=np.loadtxt(f,dtype=swf_dtype,comments=";")
            return data
        #data = np.recfromcsv(filename,delimiter=None)
        #return data


