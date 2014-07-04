library(ggplot2)
source("common.R")
source('verbose.R')

queue_size<- function(swf)
{
	verb('entering queue_size.R')
	# get start time of the jobs
	start <- swf$submit_time + swf$wait_time

	# link events with cores number (+/-)
	submits <- cbind(swf$submit_time, swf$proc_req)
	starts <- cbind(start, -swf$proc_req) 

	#   submits <- cbind(swf$submit_time, swf$proc_alloc)
	#   starts <- cbind(start, -swf$proc_alloc) 

	# because jobs still queued have an -1 wait_time
	starts[which(swf$wait_time == -1)] = max(starts) + 1

	# make one big dataframe
	U  <- rbind(submits, starts)
	colnames(U) <- c("timestamp","cores_instant")
	U <- as.data.frame(U)

	# merge duplicate rows by summing the cores nb modifications
	U <- aggregate(U$cores_instant, list(timestamp=U$timestamp), sum)

	# make a cumulative sum over the dataframe
	U <- cbind(U[,1],cumsum(U[,2]))
	colnames(U) <- c("timestamp","cores_queued")
	U <- as.data.frame(U)

	# add a new column: dates
	U <- cbind(U, timestamp_to_date(U$timestamp))
	colnames(U) <- c("timestamp","cores_queued","date")
	U <- as.data.frame(U)

	# return the dataframe
	U

}

queue_size_subset <- function(data, date_start, date_stop){
	queue = queue_size(data)
	start = date_to_timestamp(date_start)
	stop = date_to_timestamp(date_stop)

	queue_outside_begin_index = max(which(queue$timestamp <= start))
	queue_inside_end_index = max(which(queue$timestamp <= stop))

	attach(queue)
	trace_start_cores = cores_queued[queue_outside_begin_index]
	trace_stop_cores = cores_queued[queue_inside_end_index]
	detach(queue)

	queue = subset(queue, subset=(timestamp >= start & timestamp <= stop))

	first_row = data.frame(timestamp=start, cores_queued=trace_start_cores, date=timestamp_to_date(start))
	last_row = data.frame(timestamp=stop, cores_queued=trace_stop_cores, date=timestamp_to_date(stop))

	if(start == stop){
		queue = first_row
	}

	if(start != stop){
		queue = rbind(first_row, queue)
		queue = rbind(queue, last_row)
	}
	queue
}


queue_jobs_length<- function(swf)
{
	# get start time of the jobs
	start <- swf$submit_time + swf$wait_time

	# link events with jobs number (+/-)
	submits <- cbind(swf$submit_time, +1)
	starts <- cbind(start, -1) 

	# because jobs still queued have an -1 wait_time
	starts[which(swf$wait_time == -1)] = max(starts) + 1

	# make one big dataframe
	U  <- rbind(submits, starts)
	colnames(U) <- c("timestamp","nb_jobs")
	U <- as.data.frame(U)

	# merge duplicate rows by summing the jobs nb modifications
	U <- aggregate(U$nb_jobs, list(timestamp=U$timestamp), sum)

	# make a cumulative sum over the dataframe
	U <- cbind(U[,1],cumsum(U[,2]))
	colnames(U) <- c("timestamp","nb_jobs")
	U <- as.data.frame(U)

	# add a new column: dates
	U <- cbind(U, timestamp_to_date(U$timestamp))
	colnames(U) <- c("timestamp","nb_jobs","date")
	U <- as.data.frame(U)

	# return the dataframe
	U

}

queue_jobs_length_subset <- function(data, date_start, date_stop){
	queue = queue_jobs_length(data)
	start = date_to_timestamp(date_start)
	stop = date_to_timestamp(date_stop)

	queue_outside_begin_index = max(which(queue$timestamp <= start))
	queue_inside_end_index = max(which(queue$timestamp <= stop))

	attach(queue)
	trace_start_jobs = nb_jobs[queue_outside_begin_index]
	trace_stop_jobs = nb_jobs[queue_inside_end_index]
	detach(queue)

	queue = subset(queue, subset=(timestamp >= start & timestamp <= stop))

	first_row = data.frame(timestamp=start, nb_jobs=trace_start_jobs, date=timestamp_to_date(start))
	last_row = data.frame(timestamp=stop, nb_jobs=trace_stop_jobs, date=timestamp_to_date(stop))

	if(start == stop){
		queue = first_row
	}

	if(start != stop){
		queue = rbind(first_row, queue)
		queue = rbind(queue, last_row)
	}
	queue
}

graph_queue_size <- function(swf){
	queue = queue_size(swf)
	plot_queue <- ggplot(data=queue,mapping=aes(x=date,y=cores_queued, ymin=0)) +
	#geom_line() +
	geom_step() +
	theme_bw() +
	opts(
	     panel.background = theme_rect(fill = "white", colour = NA),
	     axis.title.x = theme_text(face="bold", size=12),
	     axis.title.y = theme_text(face="bold", size=12, angle=90),
	     panel.grid.major = theme_blank(),
	     panel.grid.minor = theme_blank(),
	     title="System Queue Size")

	# return the graph
	plot_queue
}

graph_queue_jobs_length <- function(swf){
	queue = queue_jobs_length(swf)
	plot_queue <- ggplot(data=queue,mapping=aes(x=date,y=nb_jobs, ymin=0)) +
	#geom_line() +
	geom_step() +
	theme_bw() +
	opts(
	     panel.background = theme_rect(fill = "white", colour = NA),
	     axis.title.x = theme_text(face="bold", size=12),
	     axis.title.y = theme_text(face="bold", size=12, angle=90),
	     panel.grid.major = theme_blank(),
	     panel.grid.minor = theme_blank(),
	     title="System Queue Length")

	# return the graph
	plot_queue
}

verb('sourced queue.R')
