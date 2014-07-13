library(ggplot2)
source("common.R")

########################
### FUNCTIONNAL PART ###
########################
ecdf_response_time <- function(swf){
        swf = subset(swf, run_time!=-1)
        swf = subset(swf, wait_time!=-1)
        response_time = swf$wait_time + swf$run_time
        cdf = ecdf(response_time)
        plot(cdf)
}
########################
ecdf_run_time <- function(swf){
        swf = subset(swf, run_time!=-1)
        cdf = ecdf(swf$run_time)
        plot(cdf)
}
########################
graph_cdf_wait_time <- function(swf){
        swf = subset(swf, wait_time!=-1)
        x=unique(swf$wait_time)
        y= ecdf(swf$wait_time)(unique(swf$wait_time))
        cdf_wt = qplot(x,y)+
        scale_x_continuous('Wait Time') + scale_y_continuous('CDF')+
        geom_line() 

        # return the graph
        cdf_wt
}
########################
