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


graph_reqtime_vs_runtime_marginal_distributions_compare_densities <- function(swf, utilization_start=0,high_treshold=100000){
  swf2=swf[which(swf$run_time<=high_treshold),]
  swf2=swf2[which(swf2$time_req<=high_treshold),]
  table1<- data.frame( value=as.numeric(swf2$time_req),type= "reqtime")
  table2<- data.frame( value=as.numeric(swf2$run_time),type= "runtime")
  table<- rbind(table1,table2)
  pp<-ggplot(data=rbind(table1,table2), aes(x=value)) +geom_density(aes(fill=type),alpha=0.2)+
  theme_bw()+
  ggtitle("Reqtime and Runtime Marginal Histograms")
  return(pp)
}


graph_reqtime_vs_runtime_marginal_distributions_compared <- function(swf, utilization_start=0,by=10000,high_treshold=100000){
  swf2=swf[which(swf$run_time<=high_treshold),]
  swf2=swf2[which(swf2$time_req<=high_treshold),]
  table1<- data.frame( value=as.numeric(swf2$time_req),type= "reqtime")
  table2<- data.frame( value=as.numeric(swf2$run_time),type= "runtime")
  table<- rbind(table1,table2)
  pp<-ggplot(data=rbind(table1,table2),aes(x=value)) +geom_histogram(aes(fill=type), position="dodge")+
  theme_bw()+
  ggtitle("Walltime and Runtime Marginal Histograms")
  return(pp)
}

graph_reqtime_vs_runtime_ratio_histogram <- function(swf, utilization_start=0,by=0.02,runtime_low_treshold=0,runtime_high_treshold=100000){
  swf2=swf[which(swf$run_time>=runtime_low_treshold),]
  swf2=swf2[which(swf2$run_time<=runtime_high_treshold),]
  tableRatio <- data.frame(value=swf2$run_time/swf2$time_req)
  pp<-ggplot(data=tableRatio ,aes(x=value)) +
  geom_histogram(breaks=seq(0,1, by=by)) +
  theme_bw()+
  ggtitle("Histogram of the Runtime/Walltime ratio")
  return(pp)
}

graph_reqtime_vs_runtime_ratio_density <- function(swf, utilization_start=0,by=0.02,runtime_low_treshold=0,runtime_high_treshold=100000){
  swf2=swf[which(swf$run_time>=runtime_low_treshold),]
  swf2=swf2[which(swf2$run_time<=runtime_high_treshold),]
  ratios <- swf2$run_time/swf2$time_req
  ratios <- ratios[which(ratios<=1)]
  tableRatio <- data.frame(value=ratios)
  pp<-ggplot(data=tableRatio ,aes(x=value)) +
  geom_density() +
  theme_bw()+
  ggtitle("Histogram of the Runtime/Walltime ratio")
  return(pp)
}

graph_reqtime_vs_runtime_ratio_per_user <- function(swf, utilization_start=0,by=0.02,runtime_low_treshold=0,runtime_high_treshold=100000){
  swf2=swf[which(swf$run_time>=runtime_low_treshold),]
  swf2=swf2[which(swf2$run_time<=runtime_high_treshold),]
  swf2$ratio<-swf2$run_time/swf2$time_req
  pp <- ggplot()+
  geom_boxplot(data=swf2, aes(factor(user_id), ratio))+
  theme_bw()+
  ggtitle("Histogram of the Runtime/Walltime ratio")
  return(pp)
}

graph_reqtime_vs_runtime_expzoom_ratio_histogram <- function(swf, utilization_start=0,by=0.02){
  swf2=swf[which(swf$run_time-swf$time_req<200),]
  swf2=swf[which(swf$time_req>=0),]
  tableRatio <- data.frame(value=(1-exp(-10*swf2$run_time/swf2$time_req)))
  pp<-ggplot(data=tableRatio ,aes(x=value)) +
  geom_histogram(breaks=seq(0,1, by=by)) +
  theme_bw()+
  ggtitle("Histogram of (1- exp(-10*Runtime/Walltime))")
  return(pp)
}


graph_reqtime_vs_runtime_heatmap <- function(swf, utilization_start=0,binwidth,xlimits,ylimits){
  swf2=swf[which(swf$run_time-swf$time_req<200),]
  pp<-ggplot(swf2,aes(x=time_req,y=run_time) ) +
  stat_binhex(binwidth = binwidth ) +
  scale_x_continuous(limits=xlimits) +
  scale_y_continuous(limits=ylimits) +
  theme_bw() +
  ggtitle("Heatmap of the Runtime vs Walltime")
  return(pp)
}


graph_cores_vs_runtime_heatmap <- function(swf, utilization_start=0,binwidth,xlimits,ylimits){
  swf2=swf[which(swf$time_req>=0),]
  swf2=swf2[which(swf$run_time-swf$time_req<=0),]
  pp<-ggplot(swf2,aes(x=proc_req,y=run_time) ) +
  stat_binhex(binwidth = binwidth ) +
  scale_x_continuous(limits=xlimits) +
  scale_y_continuous(limits=ylimits) +
  theme_bw() +
  ggtitle("Heatmap of the Cores vs Runtime")
  return(pp)
}



graph_reqtime_vs_runtime_heatmap_log10scale <- function(swf, utilization_start=0,binwidth,xlimits,ylimits){
  swf2=swf[which(swf$run_time-swf$time_req<200),]
  swf2=swf2[which(swf2$time_req>=0),]
  swf2$log10_reqtime=log10(1+swf2$time_req)
  swf2$log10_runtime=log10(1+swf2$run_time)
  #summary(swf2)
  pp<-ggplot(swf2,aes(x=log10_reqtime,y=log10_runtime) ) +
  stat_binhex(binwidth = binwidth ) +
  scale_x_continuous(limits=xlimits) +
  scale_y_continuous(limits=ylimits) +
  theme_bw() +
  ggtitle("Heatmap of the Runtime vs Walltime (log10scale)")
  return(pp)
}


verb('sourced analysis.R')
