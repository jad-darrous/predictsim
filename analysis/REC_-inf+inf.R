#!/usr/bin/Rscript


################WORKING DIRECTORY MAGIC##########
##################DO NOT ALTER###################
initial.options <- commandArgs(trailingOnly = FALSE)
file.arg.name <- "--file="
script.name <- sub(file.arg.name, "", initial.options[grep(file.arg.name, initial.options)])
script.basename <- dirname(script.name)
execution_wd=getwd()
setwd(script.basename)
base_script_wd=getwd()
###################END BLOCK#####################

##############COMMON REQUIREMENTS################
##################DO NOT ALTER###################
#Parser file with all the parser types.
source('Rscript/parser.R')
###################END BLOCK#####################


##############SCRIPT PARAMETERS##################
#############MODIFY AS REQUIRED##################

#Path file for setting up the location of your R files.
#you can alternatively set rfold='/path/to/your/files', but its less modular.
source('Rscript/path.R')

#description and epilog for the console help output.
#e.g. description="This scripts does this and that."
#e.g. epilog="use with caution. refer to www.site.com .."
description=''
epilog=''

#External parser function: for usual options.
#e.g. parser=parser_swf(description,epilog)
parser=parser_pred(description,epilog)


#additional argparse entries for this particular script.
#e.g. parser$add_argument('-s','--sum', dest='accumulate', action='store_const', const=sum, default=max,help='sum the integers (default: find the max)')

#files you want to source from the rfold folder for this Rscript
#e.g. c('common.R','histogram.R')
userfiles=c()

###################END BLOCK#####################


###SOURCING, CONTEXT CLEANING, ARG RETRIEVE######
##################DO NOT ALTER###################
#code insertion.
rm(list=setdiff(ls(),c("parser","rfold","userfiles","execution_wd","base_script_wd")))
args=parser$parse_args()
#Verbosity management.
source('Rscript/verbosity.R')
verb<-verbosity_function_maker(args$verbosity)
verb(args,"Parameters to the script")

setwd(rfold)
rfold_wd=getwd()
for (filename in userfiles) {
	source(filename)
}


setwd(base_script_wd)
rm(parser,rfold,userfiles)
###################END BLOCK#####################


#####################OUTPUT_MANAGEMENT###########
################MODIFY IF NEEDED####################
source('Rscript/output_management.R')
options_vector=set_output(args$device,args$output,args$ratio,execution_wd)
###################END BLOCK#####################


#############BEGIN YOUR RSCRIPT HERE.############
#here is your working directory :)
setwd(execution_wd)
#You have access to:
#set_output(device='pdf',filename='tmp.pdf',ratio=1)
#use it if you really want to change the output type on your way.
#pause_output(pause=TRUE) for x11
#use it to pause for output.
#args for retrieving your arguments.
library('plyr')
library('ggplot2')


#type stuff here.
plot_rec_curves <- function(preds,true_values,labelnames){
  true_runtime=ldply(true_values,data.frame)
  colnames(true_runtime)<-c("value")
  preds_dfs=data.frame()

  for (i in 1:length(preds)){
    d=ldply(preds[i],data.frame)

    d$value=labelnames[i]
    colnames(d)<-c("value","type")
    d$value=true_runtime$value-d$value
    #print(typeof(d))
    #print(class(d))

    #print(summary(d))
    preds_dfs=rbind(preds_dfs,d)
  }

  print(summary(preds_dfs))
  p0 = ggplot(preds_dfs, aes(x = value)) +
   stat_ecdf(aes(group = type, colour = type))
  print(p0)

  #m <- ggplot(d, aes(x=value))
  #m +
  #geom_density(aes(group=type,fill=type),adjust=4, colour="black",alpha=0.2,fill="gray20")+
  #coord_trans(y = "sqrt")+
  #scale_x_continuous(breaks=seq(from=0,to=86400,by=3600),labels=seq(from=0,to=24,by=1))+
  #xlab("Absolute error (hours)")+
  #ylab("Density")+
  #ggtitle("Kernel density estimation of the absolute error.")+
  #annotate("text",x=12500,y=0.000025,label="Random Forest",size=5)+
  #annotate("text",x=4500,y=0.0003,label="Baseline",size=5)+
  #theme_bw()
}

print(args$pred_filenames)
data=lapply(args$pred_filenames,read.table)
plot_rec_curves(preds=data[-1],true_values=data[1],labelnames=args$pred_filenames[-1])
print(args$pred_filenames)

###################END BLOCK#####################

#############X11 OUTPUT MANAGEMENT###############
#################MODIFY IF NEEDED################
pause_output(options_vector)
###################END BLOCK#####################


