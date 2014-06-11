source('analysis.R')
source('utilization.R')
source('standard_label.R')
source('verbose.R')
require(plotrix)
require(reshape2)

df2glesserchart<- function(data_)
{

    max_cores <<- max(utilization(data_)['cores_used'])

    data = arrange(data_, submit_time)
    # get start time and stop time of the jobs
    submi <- data$submit_time
    start <- data$submit_time + data$wait_time
    stop <- data$submit_time + data$wait_time+ data$run_time

    U = cbind(submi, start, stop, data$proc_alloc, data$job_id, data$user_id)
    colnames(U) <- c("submit","start", "stop", "cores", "id","user")
    U <- as.data.frame(U)

    #TODO: duplicate jobs that have more than one core

    U=U[with(U, order(start)), ]

    #Harmonize labels with gantt chart.
    lablength=max(nchar(as.character(max(U$id))),nchar(as.character(max_cores)))
    U$labels=standard_label(U$id,lablength)
    U$starts=U$start
    U$ends=U$stop
    U$priorities=U$user+1
    Q=U
    Q$ends=U$start
    Q$starts=U$submit
    Q$priorities=666
    D=rbind(U,Q)

    height=sum(U$cores)
    tstart=min(start)
    tstop=max(stop)

    gdf=as.list(D[,c("labels","starts","ends","priorities","cores")])

    plot(c(tstart,tstop),c(0,height),xlab="time",ylab="machines",type="n")
    axis(1, at=tstart:tstop, labels=tstart:tstop)

    y=height
    needreset=TRUE
    for (i in 1:length(gdf$cores)){
        prio<-gdf$priorities[i]
        if (prio==666){
            if (needreset){
                y=height
                needreset=FALSE
            }
            rcol="#00000000"
        }else{
            rcol=rainbow(max(U$priorities))[prio]
        }

        xleft<-gdf$starts[i]
        xright<-gdf$ends[i]
        ytop<-y
        y<-y-gdf$cores[i]
        ybottom<-y
        rect(xleft, ybottom, xright, ytop,cex=2,
             border="black",density=NA, lwd=1,col=rcol)
        if (needreset){
            text(xleft,ytop,adj=c(0,1),labels=paste("job ",gdf$labels[i]),cex=0.7)
        }
        
    }


}
df2gantt<- function(data_)
{

    max_cores <<- max(utilization(data_)['cores_used'])

    data = arrange(data_, submit_time)
    # get start time and stop time of the jobs
    submi <- data$submit_time
    start <- data$submit_time + data$wait_time
    stop <- data$submit_time + data$wait_time+ data$run_time

    U = cbind(submi, start, stop, data$proc_alloc, data$job_id, data$user_id)
    colnames(U) <- c("submit","start", "stop", "cores", "id","user")
    U <- as.data.frame(U)

    #TODO: duplicate jobs that have more than one core

    #Affect a processor to each job in the gantt. We don't know the actual processor in the system, of course.

    V=NULL
    #Harmonize labels with glesser chart.
    for (i in 1:nrow(U)){
        nc=U$cores[i]
        while (nc>1){
            nc=nc-1
            l=U[i,]
            l$cores=1
            V=rbind(V,l)
        } 
    }
            
    U=rbind(U,V)
    print(U)
    cores_vector=c()
    for (i in 1:max_cores){
        cores_vector[i]=0
    }
    U=U[with(U, order(start)), ]

    for (i in 1:length(U$id))
    {
        for (j in 1:max_cores){
            if (cores_vector[j]<=U[i,"start"]){
                cores_vector[j]=U[i,"stop"]
                U[i,"ganttcore"]=j
                break
            }
        }
    }


    
    lablength=max(nchar(as.character(max(U$id))),nchar(as.character(max_cores)))
    U$labels=standard_label(U$ganttcore,lablength)
    U$starts=U$start
    U$ends=U$stop
    U$priorities=U$user+1
    
    tstart=min(start)
    tstop=max(stop)

    gdf=as.list(U[,c("cores","labels","starts","ends","priorities","ganttcore","id")])
    print(U)

    #gantt.chart(gdf,vgridlab=tstart:tstop,vgridpos=tstart:tstop,half.height=0.5,border.col="black",xlab="System Time",main="Job execution Gantt Chart",priority.label="Users",priority.extremes=c("",""),taskcolors=rainbow(max(U$priorities)),label.cex=0.8,priority.legend=TRUE,xlim=c(tstart,tstop+(tstop-tstart)/8))

    plot(c(tstart,tstop),c(0,max_cores),xlab="time",ylab="jobs",type="n")
    axis(1, at=tstart:tstop, labels=tstart:tstop)

    needreset=TRUE
    for (i in 1:length(gdf$cores)){
        prio<-gdf$priorities[i]
        rcol=rainbow(max(U$priorities))[prio]

        xleft<-gdf$starts[i]
        xright<-gdf$ends[i]
        ytop<-gdf$ganttcore[i]
        ybottom<-ytop-1
        rect(xleft, ybottom, xright, ytop,cex=2,
             border="black",density=NA, lwd=1,col=rcol)
        if (needreset){
            text((xright+xleft)/2,(ybottom+ytop)/2,labels=gdf$id[i],cex=1.3)
        }
        
    }


}

verb('sourced visu.R')
