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
parser=parser_rf(description,epilog)


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

df <- read.table(args$filename,comment.char=';')
names(df) <- c('force')
gid=length(df$force)-11-582-7-2
#df$name=c("proc_req","time_req","tsafir_mean","last_runtime","last_runtime2","thinktime","running_maxlength","running_sumlength","amount_running","running_average_runtime","running_allocatedcores",rep("uid",582),rep("gid",gid),rep("dow",7),rep("status",1),rep("status2",1))
df$name=c("1","2","3","4","5","6","7","8","9","10","11",rep("12",582),rep("13",gid),rep("14",7),rep("15",1),rep("16",1))
uidf=sum(df[which(df$name=="12"),]$force)
gdf=sum(df[which(df$name=="13"),]$force)
dow=sum(df[which(df$name=="14"),]$force)
newrow = c(1:4)
df=df[which(df$name!="12"  & df$name!="13" &df$name!="14"),]
df = rbind(df,c(uidf,"12"))
df = rbind(df,c(gdf,"13"))
df = rbind(df,c(dow,"14"))
df$force=as.numeric(df$force)

summary(df$force)

library("ggplot2")
#ggplot(df[which(df$name != "uid" & df$name !="gid"),], aes(x = factor(1),y=force, fill = name)) +
#geom_bar(width=1,stat="identity")
#coord_polar(theta = "x")


#pause_output(options_vector)
ggplot(df, aes(x = name,y=force)) +
#geom_bar()
geom_bar(stat="identity")+xlab("Attribute")+ylab("Importance")+ggtitle("Relative Importance of Attributes")+
theme_bw()
#geom_bar(width=1,stat="identity")+
#coord_polar(theta = "y")


#type stuff here.

###################END BLOCK#####################


#############X11 OUTPUT MANAGEMENT###############
#################MODIFY IF NEEDED################
pause_output(options_vector)
###################END BLOCK#####################


