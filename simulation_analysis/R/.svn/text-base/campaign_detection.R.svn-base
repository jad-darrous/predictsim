#This script is a campaign detection tool for post-simulator swf files.
source('verbose.R')


swf_campaign_detection<-function(data){
	verb("entering swf_campaign_detection")


		submi <- data$submit_time
		start <- data$submit_time + data$wait_time
		stop <- data$submit_time + data$wait_time+ data$run_time
		U = cbind(submi, start, stop, data$proc_alloc, data$job_id, data$user_id)
		colnames(U) <- c("submit","start", "stop", "cores", "id","user")
		U <- as.data.frame(U)

		C<-as.data.frame(matrix(0, ncol = 7, nrow = 0))
		colnames(C)<-c("user","c_id","submit","end","weight","longest_job_length","job_count")

		c_counter=1
		while(nrow(U)!=0){
			j=U[1,]
			submit_time=j$submit
			user=j$user
			
			extracted_jobs=U[U$submit==submit_time & U$user==user,]
			extracted_id=extracted_jobs$id
			camp_end=max(extracted_jobs$stop)
			longest_job_length=max(extracted_jobs$stop-extracted_jobs$start)
			job_count=nrow(extracted_jobs)

			U<-U[U$submit!=submit_time|U$user!=user,]
			c_w<-0
			
			for (i in 1:nrow(extracted_jobs)){
				c_w<-c_w+extracted_jobs[i,"cores"]*(extracted_jobs[i,"stop"]-extracted_jobs[i,"start"])
			}

			
			C[nrow(C)+1,] <-c(j$user,c_counter,j$submit,camp_end,c_w,longest_job_length,job_count)
			c_counter<-c_counter+1
		}


		C$user=C$user+1
		return(C)


}


verb('sourced campaign_detection.R')
