library(ggplot2)
source('verbose.R')
source('theme.R')


plot_user_individual_stretches<-function(...,labelnames=FALSE,logscale=TRUE,xlabel="User",ylabel="Stretch",colwidth=0.3,labelstitle="Log ID",bw=FALSE){
    #input: dataframes with column names "user","stretch"
    verb("entering plot_user_individual_stretches")

    Uv <- c(...)

    if (length(labelnames)==1){
        if (labelnames==FALSE) {
            labelnames=sapply(list(1:length(Uv)),function(x){return(paste("log n°",x))})
        }	
    }

    for (i in 1:length(Uv)){
        Uv[[i]]$Logname=labelnames[i]
    }


    treshold_stretch_min <- function( U ) {
        if (nrow(U[U$stretch<1.02,])!=0){
            U[U$stretch<1.02,]$stretch=1.02
        }
        return(U)
    }

    Uv=lapply(Uv,treshold_stretch_min)

    Udf=do.call(rbind,Uv)
    verb(Udf,d="Plotting...")



    ggobj<-ggplot(data=Udf,aes(x=user,y=stretch,fill=Logname), width=colwidth)+
    geom_bar(stat='identity',position=position_dodge())+xlab(xlabel)+ylab(ylabel)+
    scale_x_continuous(breaks=c(1:max(unlist(lapply(Uv,nrow)))))




    if ( logscale ) {
        ggobj<-ggobj+scale_y_log10(breaks=c(1,10,100,1000) )
    }
    if ( bw ) {
        ggobj<-ggobj+scale_fill_grey(name=labelstitle) 
    }


    return(ggobj)

}


plot_user_stretch_hist_large_scale<-function(...,labelnames=FALSE,xlabel="Stretch Range",ylabel="Stretch Count",colwidth=0.3,labelstitle="Log ID",bw=FALSE){
    verb('entering plot_user_stretch_hist')
    #input: dataframes with column name "stretch"

    Cv <- c(...)

    if (length(labelnames)==1){
        if (labelnames==FALSE) {
            labelnames=sapply(list(1:length(Cv)),function(x){return(paste("log n°",x))})
        }	
    }


    for (i in 1:length(Cv)){
        Cv[[i]]$Logname=labelnames[i]
    }

    Categvector=c(100,200,300,400,500,600,1000,5000,10000)
    Scat=lapply(Categvector,as.character)
    Limits=c(paste("1-",Scat[1],sep=""),paste(Scat[1],"-",Scat[2],sep=""),paste(Scat[2],"-",Scat[3],sep=""),paste(Scat[3],"-",Scat[4],sep=""),paste(Scat[4],"-",Scat[5],sep=""),paste(Scat[5],"-",Scat[6],sep=""),paste(Scat[6],"-",Scat[7],sep=""),paste(Scat[7],"-",Scat[8],sep=""),paste(Scat[8],"-",Scat[9],sep=""),paste("over ",Scat[9],sep=""))
    Categ <-function(stretch){
        stretch$Category=c(1:nrow(stretch))
        for (i in 1:nrow(stretch)){
            s= stretch[i,]$stretch
            cat=""
            if (s<Categvector[1]){
                cat=paste("1-",Scat[1],sep="")
            }else if (s<Categvector[2]){
                cat=paste(Scat[1],"-",Scat[2],sep="")
            }else if (s<Categvector[3]){
                cat=paste(Scat[2],"-",Scat[3],sep="")
            }else if (s<Categvector[4]){
                cat=paste(Scat[3],"-",Scat[4],sep="")
            }else if (s<Categvector[5]){
                cat=paste(Scat[4],"-",Scat[5],sep="")
            }else if (s<Categvector[6]){
                cat=paste(Scat[5],"-",Scat[6],sep="")
            }else if (s<Categvector[7]){
                cat=paste(Scat[6],"-",Scat[7],sep="")
            }else if (s<Categvector[8]){
                cat=paste(Scat[7],"-",Scat[8],sep="")
            }else if (s<Categvector[9]){
                cat=paste(Scat[8],"-",Scat[9],sep="")
            }else{
                cat=paste("over ",Scat[9],sep="")
            }
            stretch[i,]$Category=cat
        }
        return(stretch)
    }

    Cv<-lapply(Cv,Categ)

    Cdf<-do.call(rbind,Cv)
    verb(Cdf,d="Plotting...")



    ggobj<-ggplot(data=Cdf,aes(x=Category,fill=Logname), width=colwidth)+
    geom_bar(position=position_dodge())+
    xlab(xlabel)+
    ylab(ylabel)+
    scale_x_discrete(limits=Limits)

    if ( bw ) {
        ggobj<-ggobj+scale_fill_grey(name=labelstitle) 
    }

    return(ggobj)

}




#plot_user_stretch_hist<-function(...,labelnames=FALSE,logscale=TRUE,xlabel="User",ylabel="Stretch",colwidth=0.3,labelstitle="Log ID",bw=FALSE){
    ##input: dataframes with column names "user","stretch"
    #verb("entering plot_user_individual_stretches")

    #Uv <- c(...)

    #if (length(labelnames)==1){
        #if (labelnames==FALSE) {
            #labelnames=sapply(list(1:length(Uv)),function(x){return(paste("log n°",x))})
        #}	
    #}

    #for (i in 1:length(Uv)){
        #Uv[[i]]$Logname=labelnames[i]
    #}


    #treshold_stretch_min <- function( U ) {
        #if (nrow(U[U$stretch<1.02,])!=0){
            #U[U$stretch<1.02,]$stretch=1.02
        #}
        #return(U)
    #}

    #Uv=lapply(Uv,treshold_stretch_min)

    #Udf=do.call(rbind,Uv)
    #verb(Udf,d="Plotting...")

    #ggobj<-ggplot(data=Udf,aes(stretch,fill=Logname), width=colwidth)+
    #geom_histogram(position=position_dodge())+xlab(xlabel)+ylab(ylabel)
    ##scale_x_continuous(breaks=c(1:max(unlist(lapply(Uv,nrow)))))

    #if ( logscale ) {
        #ggobj<-ggobj+scale_y_log10(breaks=c(1,10,100,1000) )
    #}
    #if ( bw ) {
        #ggobj<-ggobj+scale_fill_grey(name=labelstitle) 
    #}

    #return(ggobj)

#}


plot_user_stretch_density_large_scale<-function(...,labelnames=FALSE,xlabel="Stretch ",ylabel="Stretch log Density",colwidth=0.3,labelstitle="Log ID",bw=FALSE){
    verb('entering plot_user_stretch_hist')
    #input: dataframes with column name "stretch"

    Cv <- c(...)

    if (length(labelnames)==1){
        if (labelnames==FALSE) {
            labelnames=sapply(list(1:length(Cv)),function(x){return(paste("log n°",x))})
        }	
    }

    for (i in 1:length(Cv)){
        Cv[[i]]$Logname=labelnames[i]
    }

    Cdf<-do.call(rbind,Cv)
    verb(Cdf,d="Plotting...")

    ggobj<-ggplot(data=Cdf,aes(stretch,fill=Logname), width=colwidth)+
    geom_density(alpha = 0.2)+
    xlab(xlabel)+
    ylab(ylabel)+
    #scale_x_discrete(limits=c(100,150,200,250,300,400,500,600,800,1000))+
    xlim(c(0,1000))


    if ( bw ) {
        ggobj<-ggobj+scale_fill_grey(name=labelstitle) 
    }

    return(ggobj)

}

plot_user_stretch_density<-function(...,upperbound=100,labelnames=FALSE,xlabel="Stretch ",ylabel="Stretch Density",colwidth=0.3,labelstitle="Log ID",bw=FALSE){
    verb('entering plot_user_stretch_hist')
    #input: dataframes with column name "stretch"

    Cv <- c(...)

    if (length(labelnames)==1){
        if (labelnames==FALSE) {
            labelnames=sapply(list(1:length(Cv)),function(x){return(paste("log n°",x))})
        }	
    }

    for (i in 1:length(Cv)){
        Cv[[i]]$Logname=labelnames[i]
    }
    
    print(Cv)

    Cdf<-do.call(rbind,Cv)
    verb(Cdf,d="Plotting...")

    ggobj<-ggplot(data=Cdf,aes(stretch,fill=Logname), width=colwidth)+
    geom_density(alpha = 0.2)+
    xlab(xlabel)+
    ylab(ylabel)+
    xlim(c(0,1.5))

    if ( bw ) {
        ggobj<-ggobj+scale_fill_grey(name=labelstitle) 
    }

    return(ggobj)

}
verb('sourced campaign_analysis.R')
