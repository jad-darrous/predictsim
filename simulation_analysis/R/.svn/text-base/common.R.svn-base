source('verbose.R')
swf_read <- function(f)
{
	verb('entering swf_read')
    	df <- read.table(f,comment.char=';')
    	names(df) <- c('job_id','submit_time','wait_time','run_time','proc_alloc','cpu_time_used','mem_used','proc_req','time_req','mem_req','status','user_id','group_id','exec_id','queue_id','partition_id','previous_job_id','think_time')
	return(df)


}

df_write <- function(swf, filepath, MaxProcs=-1, UnixStartTime=-1, Note='No.')
{
	#header
	cat(paste("; Note:", Note, "\n"), file=filepath)
	if(MaxProcs!=-1)
		cat(paste("; MaxProcs: ", MaxProcs, "\n", sep = ""), file=filepath, append=TRUE)
	if(UnixStartTime!=-1)
		cat(paste("; UnixStartTime: ", UnixStartTime, "\n", sep = ""), file=filepath, append=TRUE)
	#data
	write.table(swf, filepath, row.names = FALSE, col.names = FALSE, append=TRUE)
}

verb('sourced common.R')
