library(ggplot2)
source("common.R")
source('verbose.R')

########################
### FUNCTIONNAL PART ###
########################

# TODO: when a job is not finished or still in queue at the end of the swf file,
#       the following function can give wrong results
nb_users_running_jobs <- function(swf){
	verb('entering nb_users_running_jobs')
    uid = swf$user_id
    start = swf$submit_time + swf$wait_time

    table <- cbind(start, uid)

    colnames(table) <- c("timestamp","uid")
    table <- as.data.frame(table)

    table <- aggregate(table$uid, list(timestamp=table$timestamp), length)
    colnames(table) = c("timestamp", "users")
    table

}

nb_users_running_jobs_subset <- function(data, date_start, date_stop){
        nb_users_running_jobs = nb_users_running_jobs(data)
        start = date_to_timestamp(date_start)
        stop = date_to_timestamp(date_stop)

        nb_users_running_jobs_outside_begin_index = max(which(nb_users_running_jobs$timestamp <= start))
        nb_users_running_jobs_inside_end_index = max(which(nb_users_running_jobs$timestamp <= stop))
        
        attach(nb_users_running_jobs)
        trace_start_users = users[nb_users_running_jobs_outside_begin_index]
        trace_stop_users = users[nb_users_running_jobs_inside_end_index]
        detach(nb_users_running_jobs)

        nb_users_running_jobs = subset(nb_users_running_jobs, subset=(timestamp >= start & timestamp <= stop))

        first_row = data.frame(timestamp=start, users=trace_start_users)
        last_row = data.frame(timestamp=stop, users=trace_stop_users)

        if(start == stop){
            running_users = first_row
        }

        if(start != stop){
            nb_users_running_jobs = rbind(first_row, nb_users_running_jobs)
            nb_users_running_jobs = rbind(nb_users_running_jobs, last_row)
        }
        nb_users_running_jobs
}
####################
### GRAPHIC PART ###
####################

graph_users_submissions <- function(swf){
	verb('entering graph_user_submissions')
        #dates = timestamp_to_date(swf$submit_time)
        uid = swf$user_id
        dates = timestamp_to_date(swf$submit_time)
        user_sub = data.frame(uid=uid, date=dates) 

        plot_users <- ggplot(data=user_sub,mapping=aes(x=date,y=uid)) +
        #geom_line() +
        geom_point() +
        theme_bw() +
        opts(
        panel.background = theme_rect(fill = "white", colour = NA),
        axis.title.x = theme_text(face="bold", size=12),
        axis.title.y = theme_text(face="bold", size=12, angle=90),
        panel.grid.major = theme_blank(),
        panel.grid.minor = theme_blank(),
        title="Users Submissions")
        # return the graph
        plot_users
}

graph_nb_users <- function(swf){
	verb('entering graph_nb_users')
        data = nb_users_running_jobs(swf)
        dates = timestamp_to_date(data$timestamp)
        nb_users = data.frame(users=data$users, date=dates) 

        plot_nb_users <- ggplot(data=nb_users,mapping=aes(x=date,y=users)) +
        #geom_line() +
        geom_line() +
        theme_bw() +
        opts(
        panel.background = theme_rect(fill = "white", colour = NA),
        axis.title.x = theme_text(face="bold", size=12),
        axis.title.y = theme_text(face="bold", size=12, angle=90),
        panel.grid.major = theme_blank(),
        panel.grid.minor = theme_blank(),
        title="Users Having Running Jobs")
        # return the graph
        plot_nb_users
}

verb('sourced users.R')
