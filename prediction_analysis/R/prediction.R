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


predict_runtime_2mean <- function(swf){
  for ( u in unique(swf$user_id) ) {
    last2=-1
    last1=-1
    for ( job in swf[which(swf$user_id=u)]   ) {
:
    }
  }
  pp<-ggplot(swf2,aes(x=time_req,y=run_time) ) +
  stat_binhex(binwidth = binwidth ) +
  scale_x_continuous(limits=xlimits) +
  scale_y_continuous(limits=ylimits) +
  theme_bw() +
  ggtitle("Heatmap of the Runtime vs Walltime")
  return(pp)
}


verb('sourced analysis.R')
