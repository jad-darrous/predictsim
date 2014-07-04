set_output<-function(device='pdf',filename='',ratio=1,execution_wd){
	if (device=='pdf'|filename!=''){
		old_wd=getwd()
		setwd(execution_wd)	
		if ( filename=='' ) {
			filename<-'tmp.pdf' 
		}
		pdf(file=filename,width=7*ratio,height=7)
		setwd(old_wd)
		return(c("nostop",FALSE))
	}else if (device=="x11"){
		x11(width=7*ratio,height=7)
		return(c("stop","tcl"))
	} else if (device=="x11-notcl"){
		x11(width=7*ratio,height=7)
		return(c("stop","wait"))
	}
}

pause_output<-function(optionsvector){
	if (optionsvector[1]!="stop"){
		return()
	}	
	if (optionsvector[2]=="tcl"){
		library(tcltk)
		tk_messageBox(message="Press ok to go to next output.")
	}else if (optionsvector[2]=="wait" ){
		message("Press return to refresh the x11 window.(click it once before!)")
		message("Type ok to go to next output.")
		dev.flush() 
		stopme<<-FALSE
		while(stopme!="ok"){
			Sys.sleep(0.01)
			dev.flush() 
			getGraphicsEvent(onKeybd=function(key){dev.off()})
			stopme=readLines("stdin", n=1)
		}
	}

}

