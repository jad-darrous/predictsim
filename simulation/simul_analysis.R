
library(plyr)




files = commandArgs(trailingOnly = TRUE)

if(length(files) < 2)
{
	print("USAGE: Rscript simul_analysis.R oupput/file.csv dir/*.swf other.swf")
	idontknowhowtoquitascript
}

output_file = files[1]
files = files[2:length(files)]






timestamp_to_date <- function(timestamp, zone="Europe/Paris"){
    return(as.POSIXct(timestamp, origin="1970-01-01 00:00.00", tz=zone)) 
}

swf2df <- function(f, trace_start=0, with_energy=FALSE)
{
    ##This function read a swf trace from a file 
    # INPUT: swf trace file
    # OUTPUT: swf dataframe
    df <- read.table(f,comment.char=';')
    if(with_energy)
	names(df) <- c('job_id','submit_time','wait_time','run_time','proc_alloc','cpu_time_used','mem_used','proc_req','time_req','mem_req','status','user_id','group_id','exec_id','queue_id','partition_id','previous_job_id','think_time','energy_consumed')
    else
	names(df) <- c('job_id','submit_time','wait_time','run_time','proc_alloc','cpu_time_used','mem_used','proc_req','time_req','mem_req','status','user_id','group_id','exec_id','queue_id','partition_id','previous_job_id','think_time')
    df$submit_time = df$submit_time + trace_start

    #max = pmax(df$proc_alloc, df$proc_req)
    #df$proc_req = df$proc_alloc = max   # set proc_req as proc_alloc if they differ. otherwise may cause troubles later
    #df$proc_req = df$proc_alloc
    #df$proc_alloc = df$proc_req

    df
}
utilization <- function(data, utilization_start=0, maxTime=NULL, measure="proc_alloc", measure_name="cores_used")
{
  data = arrange(data, submit_time)
  
  # get start time and stop time of the jobs
  start <- data$submit_time + data$wait_time
  stop <- data$submit_time + data$wait_time + data$run_time
  if(is.null(maxTime))
	maxTime = max(stop)
  # because jobs still running have an -1 runtime
  stop[which(data$run_time == -1 & data$wait_time != -1)] = maxTime
  # because jobs not scheduled yet have an -1 runtime and wait time
  stop[which(data$run_time == -1 & data$wait_time == -1)] = maxTime
  start[which(data$run_time == -1 & data$wait_time == -1)] = maxTime
  
  first_sub = min(data$submit_time)
  first_row = data.frame(timestamp=first_sub, measure_instant=utilization_start)
 
  # link events with measure number (+/-)
  startU <- cbind(start, data[[measure]])
  endU <- cbind(stop, -data[[measure]]) 

  # make one big dataframe
  U  <- rbind(startU, endU)
  colnames(U) <- c("timestamp","measure_instant")
  U <- rbind(as.data.frame(first_row), U)
  U <- as.data.frame(U)

  # merge duplicate rows by summing the measure nb modifications
  U <- aggregate(U$measure_instant, list(timestamp=U$timestamp), sum)

  # make a cumulative sum over the dataframe
  U <- cbind(U[,1],cumsum(U[,2]))                  # TODO: if goes under '0', maybe try something for discovering the utilization offset... difficult
  colnames(U) <- c("timestamp",measure_name)
  U <- as.data.frame(U)
  
  # add a new column: dates
  U <- cbind(U, timestamp_to_date(U$timestamp)) 
  colnames(U) <- c("timestamp",measure_name,"date")
  U <- as.data.frame(U)

  # return the dataframe
  U

}


#rbind transform things to levels and mess up everything
#this function correct this
convert.factors.to.strings.in.dataframe <- function(dataframe)
{
        class.data  <- sapply(dataframe, class)
        factor.vars <- class.data[class.data == "factor"]
        for (colname in names(factor.vars))
        {
            dataframe[,colname] <- as.character(dataframe[,colname])
        }
        return (dataframe)
}

readMaxProcs <- function(inputFile)
{
	con  <- file(inputFile, open = "r")

	maxProcs = ""
	while (length(oneLine <- readLines(con, n = 1, warn = FALSE)) > 0) { 
		if(substr(oneLine, 0, 11) == "; MaxProcs:")
		{
			maxProcs = oneLine;
			break;
		}
	} 
	close(con)

	t = unlist(strsplit(maxProcs, " "))
	t = as.numeric(t[3:length(t)])

	t
}





col_names = c()
results = data.frame()

for(f in files)
{
	col_names = c("file")
	result = c(f)
	
	swf_wait = swf2df(f)
	
	swf_wait$submit_time[which(swf_wait$submit_time == -1)] = Inf
	swf_wait$wait_time[which(swf_wait$wait_time == -1)] = Inf
	swf_wait$run_time[which(swf_wait$run_time == -1)] = 0
	
	# get start time and stop time of the jobs
	swf_wait$start <- swf_wait$submit_time + swf_wait$wait_time
	swf_wait$stop <- swf_wait$submit_time + swf_wait$wait_time + swf_wait$run_time
	
	swf_wait$stretch = (swf_wait$wait_time+swf_wait$run_time)/(swf_wait$run_time)
	
	col_names = c(col_names, "maxStretch")
	result = c(result, max(swf_wait$stretch))
	col_names = c(col_names, "meanStretch")
	result = c(result, mean(swf_wait$stretch))
	
	swf_wait$flow = (swf_wait$wait_time+swf_wait$run_time)
	
	col_names = c(col_names, "maxFlow")
	result = c(result, max(swf_wait$flow))
	col_names = c(col_names, "meanFlow")
	result = c(result, mean(swf_wait$flow))

	util = utilization(swf_wait)
	util_p1 = util[seq(2,nrow(util)),]
	util_p1[nrow(util),] = util_p1[nrow(util)-1,]
	util$next_t = util_p1$timestamp
	util$next_c = util_p1$cores_used
	util$int = util$cores_used*(util$next_t-util$timestamp)
	work = sum(util$int)
	col_names = c(col_names, "Work")
	result = c(result, work)
	
	completion_time = max(swf_wait$stop) - min(swf_wait$submit_time)
	col_names = c(col_names, "completion_time")
	result = c(result, completion_time)
	
	maxProcs = readMaxProcs(f)
	col_names = c(col_names, "utilization (%)")
	result = c(result, work/completion_time/maxProcs)
	
	
	col_names = c(col_names, "Jobs_Launched")
	result = c(result, nrow(swf_wait[which(swf_wait$start<Inf),]))
	
	
	results = rbind.data.frame(results, result)
	results = convert.factors.to.strings.in.dataframe(results)
	colnames(results) <- col_names
}

# print(results)
write.csv(results, file=output_file)

