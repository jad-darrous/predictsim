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
        geom_line() +
        #geom_step() +
        theme_bw() +
        opts(
        panel.background = theme_rect(fill = "white", colour = NA),
        axis.title.x = theme_text(face="bold", size=12),
        axis.title.y = theme_text(face="bold", size=12, angle=90),
        panel.grid.major = theme_blank(),
        panel.grid.minor = theme_blank(),
        title="CDF Wait Time")

        # return the graph
        cdf_wt
}
########################
