library(gridExtra)
library(plotrix)
source('utilization.R')
library(plyr)
source('verbose.R')


draw_virtual_schedule <-function(Rlist,max_users,max_cores){
    verb('entering draw_virtual_schedule')
    begin=Rlist[[1]]$begin	
    end=Rlist[[length(Rlist)]]$end+0.52



    #lablength=max(strwidth(max_users,units="inches"),strwidth(max_cores,units="inches")) + 0.3
    #par(mai=c(0.4,lablength+0.08,strheight("M",units="inches"), 0.1),omi=c(0.1, 0.1, 0.1, 0.1), xaxs = "i", yaxs = "i")

    plot(c(begin,end),c(0,max_cores),xlab="time",ylab="virtual cores",type="n")
    #segments(0,max_cores,0,0)
    axis(1, at=begin:end, labels=begin:end)




    for (i in 1:length(Rlist)){
        Rl=Rlist[[i]]
        k=nrow(Rl$users)
        h=max_cores/k
        u=0
        if (k!=0){
            for (j in 1:k){
                xleft=Rl$begin
                ybottom=u
                ytop=u+h
                xright=Rl$end
                #rect(xleft, ybottom, xright, ytop,col=Rdf[j]$user)
                rect(xleft, ybottom, xright, ytop,cex=2,lwd=22,border=NA,col=rainbow(max_users)[Rl$users[j,"id"]])
                #segments(c(xleft,xleft),c(ytop,ybottom),c(xright,xright))
                campaign_ended=Rl$users[j,"end_camp"]
                if(campaign_ended){
                    #segments(xright,ybottom,xright,ytop)
                }

                u=u+h
            }
        }
    }

    for (i in 1:length(Rlist)){
        Rl=Rlist[[i]]
        k=nrow(Rl$users)
        h=max_cores/k
        u=0
        if (k!=0){
            for (j in 1:k){
                xleft=Rl$begin
                ybottom=u
                ytop=u+h
                xright=Rl$end
                segments(c(xleft,xleft),c(ytop,ybottom),c(xright,xright))
                campaign_ended=Rl$users[j,"end_camp"]
                if(campaign_ended){
                    segments(xright,ybottom,xright,ytop)
                }

                u=u+h
            }
        }
    }
}

df2virtual_schedule <- function (data_){


    max_cores <<- max(utilization(data_)['cores_used'])

    data = arrange(data_, submit_time)
    # get start time and stop time of the jobs
    submi <- data$submit_time
    start <- data$submit_time + data$wait_time
    stop <- data$submit_time + data$wait_time+ data$run_time

    U = cbind(submi, start, stop, data$proc_alloc, data$job_id, data$user_id)
    colnames(U) <- c("submit","start", "stop", "cores", "id","user")
    U <- as.data.frame(U)

    C<-as.data.frame(matrix(0, ncol = 5, nrow = 0))
    colnames(C)<-c("user","start","weight","c_id","flagged")


    c_counter=1
    while(nrow(U)!=0){
        j=U[1,]
        submit_time=j$submit
        user=j$user

        extracted_jobs=U[U$submit==submit_time & U$user==user,]
        extracted_id=extracted_jobs$id

        U<-U[U$submit!=submit_time|U$user!=user,]
        c_w<-0

        for (i in 1:nrow(extracted_jobs)){
            c_w<-c_w+extracted_jobs[i,"cores"]*(extracted_jobs[i,"stop"]-extracted_jobs[i,"start"])
        }
        C[nrow(C)+1,] <-c(j["user"],j["submit"],c_w,c_counter)
        c_counter<-c_counter+1
    }


    C$flagged=FALSE
    C$user=C$user+1
    C=arrange(C,start)

    #begin ostrich representation computation.
    Rlist=list()
    #initiate userlist
    usercount=length(unique(C$user))
    userlist=list()
    for (i in 1:usercount){
        userlist[length(userlist)+1]=FALSE
    }
    t<-min(C$start)

    testvar=TRUE
    while (testvar){
        testvar=FALSE

        #insert camps into userlist and tag in df.
        selected_camps=C[C$flagged==FALSE & C$start==t,]
        if(nrow(selected_camps)>0){
            C[C$flagged==FALSE & C$start==t,]$flagged=TRUE
        }
        for (i in 1: nrow(selected_camps)){
            if (nrow(selected_camps)>0){
                camp=selected_camps[i,]
                if (is.logical(userlist[[camp$user]])){
                    userlist[[camp$user]]=list(camp)
                }else{
                    userlist[[camp$user]][[length(userlist[[camp$user]])+1]]=camp
                }
            }
        }
        #get user count.
        k<-0
        for (i in 1:usercount){
            if (!is.logical(userlist[[i]])){
                k<-k+1
            }
        }	

        #acquire nearest event time.	
        t1<-Inf	
        for (i in 1:usercount){
            if (!is.logical(userlist[[i]])){
                camp=userlist[[i]][[1]]
                t1=min(t1,t+(camp$weight*k/max_cores))
            }
        }
        t1=min(t1,C[C$flagged==FALSE,]$start)

        #appending the result.		
        active_users=as.data.frame(matrix(0,ncol=2,nrow=0))
        colnames(active_users)=c("id","end_camp")
        for (i in 1:usercount){
            if (!is.logical(userlist[[i]])){
                active_users[nrow(active_users)+1,]=c(i,FALSE)
            }
        }
        Rlist[[length(Rlist)+1]]=list(begin=t,end=t1,users=active_users)

        #the delta of this iteration.
        delta=max_cores*(t1-t)/k

        #update the userlist, remove campaigns and reset to FALSE if empty..
        for (i in 1:usercount){
            if (!is.logical(userlist[[i]])){
                camp=userlist[[i]][[1]]
                camp$weight=camp$weight-delta
                userlist[[i]][[1]]=camp
                if (camp$weight<0.0001){
                    userlist[[i]][[1]]=NULL		
                    R_user_entry=Rlist[[length(Rlist)]]$users[Rlist[[length(Rlist)]]$users$id==camp$user,]
                    Rlist[[length(Rlist)]]$users[Rlist[[length(Rlist)]]$users$id==camp$user,2]=TRUE
                }
                if (length(userlist[[i]])==0){
                    userlist[[i]]=FALSE
                }	
            }
        }

        #prepare for next round:
        t<-t1	
        testvar=FALSE
        if (FALSE %in% C$flagged){
            testvar=TRUE
        }	
        for(i in 1:usercount){
            if(!is.logical(userlist[[i]])){
                testvar=TRUE
            }	
        }


    }
    draw_virtual_schedule(Rlist,usercount,max_cores)
}



verb('sourced ostrich.R')
