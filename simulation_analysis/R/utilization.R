library(ggplot2)
library(plyr)
source("common.R")
source('verbose.R')

utilization <- function( data,utilization_start=0 )
{
	verb('entered utilization')

	data = arrange(data, submit_time)
	# get start time and stop time of the jobs
	start <- data$submit_time + data$wait_time
	stop <- data$submit_time + data$wait_time + data$run_time
	# because jobs still running have an -1 runtime
	stop[which(data$run_time == -1 & data$wait_time != -1)] = max(stop)
	# because jobs not schedlued yet have an -1 runtime and wait time
	stop[which(data$run_time == -1 & data$wait_time == -1)] = max(stop)
	start[which(data$run_time == -1 & data$wait_time == -1)] = max(stop)

	first_sub = min(data$submit_time)
	first_row = data.frame(timestamp=first_sub, cores_instant=utilization_start)

	# link events with cores number (+/-)
	startU <- cbind(start, data$proc_alloc)
	endU <- cbind(stop, -data$proc_alloc)

	# make one big dataframe
	U  <- rbind(startU, endU)
	colnames(U) <- c("timestamp","cores_instant")
	U <- rbind(as.data.frame(first_row), U)
	U <- as.data.frame(U)

	# merge duplicate rows by summing the cores nb modifications
	U <- aggregate(U$cores_instant, list(timestamp=U$timestamp), sum)

	# make a cumulative sum over the dataframe
	U <- cbind(U[,1],cumsum(U[,2]))                  # TODO: if goes under '0', maybe try something for discovering the utilization offset... difficult
	colnames(U) <- c("timestamp","cores_used")
	U <- as.data.frame(U)

	# return the dataframe
	return(U)


}

graph_utilization <- function(swf, utilization_start=0){
	verb('entered graph_utilization')
	table <- utilization(swf, utilization_start)
	table <- as.data.frame(table)
	print(table)
	pp <- ggplot() +
	geom_step(data=table, aes(x=timestamp, y = cores_used)) 

	return(pp)
}

#return max cores used at any moment in this log. for one or more swf data frame.
max_cores <-function(data){
	U<-utilization(data)
	return(max(U$cores_used))
}

verb('sourced utilization.R')
