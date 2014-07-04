swf_statistics<-function(df)
{
	date_to_timestamp <- function(date, zone="Europe/Paris"){
	    return(as.numeric(as.POSIXlt(date, origin="1970-01-01 01:00.00", tz=zone)))
	}

	timestamp_to_date <- function(timestamp){
	    return(as.POSIXct(timestamp, origin="1970-01-01 01:00.00", tz="Europe/Paris")) 
	}

	interval<-max(df$submit_time)-min(df$submit_time)
        print(paste("Time interval in UNIX timestamp :",interval,"Seconds"),quote=FALSE)
	months=floor(interval/(3600*24*30))
	print(paste("Time in months :",months),quote=FALSE)
        Startdate<- timestamp_to_date(min(df$submit_time))
        Enddate<- timestamp_to_date(max(df$submit_time))
        print(paste("Start Date: ",Startdate),quote=FALSE)
        print(paste("End Date: ",Enddate),quote=FALSE)
        Nsamples<-nrow(df)
        print(paste("Number of Jobs",Nsamples),quote=FALSE)
}
