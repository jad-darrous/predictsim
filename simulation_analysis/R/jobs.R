library(ggplot2)
source("common.R")
source('verbose.R')

job_arrivals<- function(swf)
{
 
	verb('entering job_arrivals')
  # link events with cores number
  U <- cbind(swf$submit_time, swf$proc_req) 
  U <- cbind(U, swf$job_id) 

  colnames(U) <- c("timestamp","cores_requested","job_id")
  U <- as.data.frame(U)
  
  # add a new column: dates
  U <- cbind(U, timestamp_to_date(U$timestamp))
  colnames(U) <- c("timestamp","cores_requested","job_id","date")
  U <- as.data.frame(U)

  # return the dataframe
  U

}
########################
job_terminations<- function(swf)
{
	verb('entering job_terminations')
  # ignore non-finished job
  swf_finished = subset(swf, wait_time != -1 & run_time!=-1)
  
  stop <- swf_finished$submit_time + swf_finished$wait_time + swf_finished$run_time
  # link events with cores number
  U <- cbind(stop, swf_finished$proc_alloc) 
  U <- cbind(U, swf_finished$job_id) 

  colnames(U) <- c("timestamp","cores_released","job_id")
  U <- as.data.frame(U)
  
  # add a new column: dates
  U <- cbind(U, timestamp_to_date(U$timestamp))
  colnames(U) <- c("timestamp","cores_released","job_id","date")
  U <- as.data.frame(U)

  # return the dataframe
  U

}
########################
job_start_impulses<- function(swf)
{
  # ignore non-started job
  swf_started = subset(swf, wait_time != -1)
  
  # get start time of the jobs
  start <- swf_started$submit_time + swf_started$wait_time
 
  # link events with cores number
  U <- cbind(start, swf_started$proc_alloc) 
  U <- cbind(U, swf_started$job_id) 

  colnames(U) <- c("timestamp","cores_starts","job_id")
  U <- as.data.frame(U)
  
  # add a new column: dates
  U <- cbind(U, timestamp_to_date(U$timestamp)) 
  colnames(U) <- c("timestamp","cores_starts","job_id","date")
  U <- as.data.frame(U)

  # return the dataframe
  U

}
########################
# TODO: when a job is not finished or still in queue at the end of the swf file,
#       the following function can give wrong results
running_jobs <- function(data, running_jobs_start=0)
{
  # get start time and stop time of the jobs
  start <- data$submit_time + data$wait_time
  stop <- data$submit_time + data$wait_time + data$run_time
  
  first_sub = min(data$submit_time)
  first_row = data.frame(timestamp=first_sub, jobs=running_jobs_start)
 
  # link events with jobs starts
  startU <- cbind(start, 1)
  endU <- cbind(stop, -1) 

  # make one big dataframe
  U  <- rbind(startU, endU)
  colnames(U) <- c("timestamp","jobs")
  U <- rbind(as.data.frame(first_row), U)
  U <- as.data.frame(U)

  # merge duplicate rows by summing the cores nb modifications
  U <- aggregate(U$jobs, list(timestamp=U$timestamp), sum)

  # make a cumulative sum over the dataframe
  U <- cbind(U[,1],cumsum(U[,2]))
  colnames(U) <- c("timestamp","jobs")
  U <- as.data.frame(U)
  
  # add a new column: dates
  U <- cbind(U, timestamp_to_date(U$timestamp)) 
  colnames(U) <- c("timestamp","jobs","date")
  U <- as.data.frame(U)

  # return the dataframe
  U

}
########################
# TODO: when a job is not finished or still in queue at the end of the swf file,
#       the following function can give wrong results
running_jobs_subset <- function(data, date_start, date_stop, running_jobs_start=0){
        running_jobs = running_jobs(data, running_jobs_start)
        start = date_to_timestamp(date_start)
        stop = date_to_timestamp(date_stop)

        running_jobs_outside_begin_index = max(which(running_jobs$timestamp <= start))
        running_jobs_inside_end_index = max(which(running_jobs$timestamp <= stop))
        
        attach(running_jobs)
        trace_start_jobs = jobs[running_jobs_outside_begin_index]
        trace_stop_jobs = jobs[running_jobs_inside_end_index]
        detach(running_jobs)

        running_jobs = subset(running_jobs, subset=(timestamp >= start & timestamp <= stop))

        first_row = data.frame(timestamp=start, jobs=trace_start_jobs, date=timestamp_to_date(start))
        last_row = data.frame(timestamp=stop, jobs=trace_stop_jobs, date=timestamp_to_date(stop))

        if(start == stop){
            running_jobs = first_row
        }

        if(start != stop){
            running_jobs = rbind(first_row, running_jobs)
            running_jobs = rbind(running_jobs, last_row)
        }
        running_jobs
}
########################
# TODO: when a job is not finished or still in queue at the end of the swf file,
#       the following function can give wrong results
running_jobs_for_timestamps_array <- function(swf_data, time_array){
    
    time_array=unique(time_array)
    
	running = running_jobs_subset(swf_data, timestamp_to_date(min(time_array)), timestamp_to_date(max(time_array)))
    	#print(running[1:10,])
	running_time = data.frame(time=time_array,jobs=1)
    for(index in 1:nrow(running))
    {

                running_to_setup = which(running_time$time < running$timestamp[index + 1] & running_time$time >= running$timestamp[index])        
                jobs = running$jobs[index]
                #print(jobs)
		running_time$jobs[running_to_setup]=jobs
    }
    running_time = as.data.frame(cbind(running_time, date = timestamp_to_date(running_time$time))) 
    running_time
}

####################
### GRAPHIC PART ###
####################
graph_job_start_impulses <- function(swf){
        starts = job_start_impulses(swf)
        plot_starts <- qplot(date, cores_starts, data = starts, geom="segment", yend = 0, xend = date) +
        #geom_point() +
        #geom_segment(aes(xend = date, yend = cores_starts)) +
        theme_bw() +
        opts(
        panel.background = theme_rect(fill = "white", colour = NA),
        axis.title.x = theme_text(face="bold", size=12),
        axis.title.y = theme_text(face="bold", size=12, angle=90),
        panel.grid.major = theme_blank(),
        panel.grid.minor = theme_blank(),
        title="Job Starts Impulses")

        # return the graph
        plot_starts
}
####################
graph_job_terminations <- function(swf){
        ends = job_terminations(swf)
        plot_term <- qplot(date, cores_released, data = ends, geom="segment", yend = 0, xend = date) +
        #geom_point() +
        #geom_segment(aes(xend = date, yend = cores_starts)) +
        theme_bw() +
        opts(
        panel.background = theme_rect(fill = "white", colour = NA),
        axis.title.x = theme_text(face="bold", size=12),
        axis.title.y = theme_text(face="bold", size=12, angle=90),
        panel.grid.major = theme_blank(),
        panel.grid.minor = theme_blank(),
        title="Job Terminations")

        # return the graph
        plot_term
}

graph_job_arrivals <- function(swf){
	verb('entering graph_job_arrivals')
        arrivals = job_arrivals(swf)
        plot_arrivals <- ggplot(data=arrivals,mapping=aes(x=date,y=cores_requested, ymin=0)) +
        #plot_arrivals <- qplot(date, cores_requested, data=arrivals, size=length(cores_requested)) +
        geom_point(alpha=0.2, size=1)
        # return the graph
        plot_arrivals
}

graph_running_jobs <- function(swf){
	verb('entering graph_running_jobs')
        runnings = running_jobs(swf)
        plot_runnings <- ggplot(data=runnings,mapping=aes(x=date,y=jobs)) +
        geom_line()       # return the graph
        plot_runnings
}

verb('sourced jobs.R')
