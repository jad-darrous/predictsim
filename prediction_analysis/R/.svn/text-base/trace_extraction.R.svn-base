## Extract a riplay-ready interval of an swf file
# This is not a real script, this is some advices given by Joseph on a mail and paste here.

source("analysis.R")

file_input = "../curie_CLEANED.swf"
trace = swf2df(file_input, 1296571124)
# date_start = "2012-10-01 09:00:00"
# date_start_ts = date_to_timestamp(date_start)
# date_stop  = "2012-10-01 12:00:00"
# date_stop_ts = date_to_timestamp(date_stop)
date_start_ts = 1335957024
date_stop_ts = 1335957024 + 3600

sub_output = "swf_curie_1335957024+1.swf"
running_output = "swf_curie_1335957024+1.swf.running"
queued_output = "swf_curie_1335957024+1.swf.queued"

util_trace = utilization(trace)

#jobs_to_submit = subset(trace, (submit_time>=date_start_ts & submit_time+wait_time+run_time<=date_stop_ts))
jobs_to_submit = subset(trace, (submit_time>=date_start_ts & submit_time<=date_stop_ts))

# nombre de cores used a une date
cores_used_at_trace_start = tail(util_trace$cores_used[which(util_trace$timestamp>=date_start_ts-3600 & util_trace$timestamp<=date_start_ts)], n=1)

# liste des jobs running a une date
running_jobs_at_trace_start = subset(trace, (submit_time+wait_time<=date_start_ts & submit_time+wait_time+run_time>date_start_ts))

# liste des jobs dans la queue a une date
queued_jobs_at_trace_start = subset(trace, (submit_time<date_start_ts & submit_time+wait_time>date_start_ts))


# on colle les 3 sous-traces dans un seul dataset pour voir
replay_trace = rbind(running_jobs_at_trace_start, queued_jobs_at_trace_start)
replay_trace = rbind(replay_trace, jobs_to_submit)


# ensuite, les jobs running doivent etre modifies: run_time et walltime reduit du delta entre leur vraie valeur et le debut de la trace
index_running_jobs = which(trace$submit_time+trace$wait_time<=date_start_ts & trace$submit_time+trace$wait_time+trace$run_time>date_start_ts)
delta = -(trace$submit_time[index_running_jobs]+trace$wait_time[index_running_jobs] - date_start_ts)
running_jobs_at_trace_start$run_time = running_jobs_at_trace_start$run_time - delta
running_jobs_at_trace_start$time_req = running_jobs_at_trace_start$time_req - delta

# on met la date de soumission a 0
running_jobs_at_trace_start$submit_time = 0
#running_jobs_at_trace_start$job_id = running_jobs_at_trace_start$job_id - min(running_jobs_at_trace_start$job_id) + 1

queued_jobs_at_trace_start$submit_time = 0
#queued_jobs_at_trace_start$job_id = queued_jobs_at_trace_start$job_id - min(queued_jobs_at_trace_start$job_id) + 1

df2swf(running_jobs_at_trace_start, running_output)
df2swf(queued_jobs_at_trace_start, queued_output)


### jobs to submit
first_job_id = min(jobs_to_submit$job_id)
unix_start_time = min(jobs_to_submit$submit_time)

jobs_to_submit$job_id = jobs_to_submit$job_id - first_job_id + 1
jobs_to_submit$submit_time = jobs_to_submit$submit_time - unix_start_time

df2swf(jobs_to_submit, sub_output, MaxProcs=80640, UnixStartTime=date_start_ts, Note=paste('Created from trace_extraction.R (',file_input,')'))


