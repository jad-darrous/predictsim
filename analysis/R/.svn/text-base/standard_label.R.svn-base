#Function for harmonizind labels between plots.
#arguments: strin- a string
#	    leng- the length to make that string (will not -reduce- a string but only add spaces.)

standard_label <-function(strin,leng)
{
	for (i in 1:length(strin)){
		if (nchar(as.character(strin[i]))<leng){
			strin[i]=standard_label(paste(" ",as.character(strin[i])),leng)	
		}else{
			strin[i]=as.character(strin[i])
		}
	}
	return(strin)
}




