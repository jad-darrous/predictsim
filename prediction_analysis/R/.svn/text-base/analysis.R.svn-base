library(plyr)
library(ggplot2)
library(gridExtra)
source("common.R")
source("utilization.R")
source("queue.R")
source("jobs.R")
source("cdf.R")
source("users.R")
source('verbose.R')


date_to_timestamp <- function(date, zone="Europe/Paris"){
	return(as.numeric(as.POSIXlt(date, origin="1970-01-01 01:00.00", tz=zone)))
}

timestamp_to_date <- function(timestamp){
	return(as.POSIXct(timestamp, origin="1970-01-01 01:00.00", tz="Europe/Paris")) 
}



graph_usage <- function(swf, utilization_start=0){
	verb('entering graph_usage')
	
	plot_util <- graph_utilization(swf, utilization_start)

	plot_queue <- graph_queue_size(swf)



	plot_arrivals <- graph_job_arrivals(swf)


	plot_ecdf_wait <- graph_cdf_wait_time(swf)

	grid.arrange(plot_util, plot_queue, plot_arrivals,  plot_ecdf_wait, ncol=2)

}

verb('sourced analysis.R')
