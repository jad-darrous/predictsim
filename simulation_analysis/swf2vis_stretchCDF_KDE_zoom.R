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
description='This tool will plot system utilization for the whole log file.'
epilog='You can input multiple swf files, they will be cat.'


#External parser function: for usual options.
#e.g. parser=parser_swf(description,epilog)
parser=parser_swf_minimal(description,epilog)


#additional argparse entries for this particular script.
#e.g. parser$add_argument('-s','--sum', dest='accumulate', action='store_const', const=sum, default=max,help='sum the integers (default: find the max)')

#files you want to source from the rfold folder for this Rscript
#e.g. c('common.R','histogram.R')
userfiles=c('common.R',"analysis.R","visu.R")
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



dfs=data.frame()
maxes=c()
means=c()

for (i in 1:length(args$swf_filenames)){
  swf_filename=args$swf_filenames[i]
  data=swf_read(swf_filename)
  value=(data$wait_time+data$run_time)/data$run_time
  means[i]=mean(value)
  maxes[i]=max(value)
  value=value[which(value>200 & value <100000)]
  d=data.frame(value=value,type=character(length(value)))
  d$type=swf_filename
  dfs=rbind(dfs,d)
}

ggplot(dfs, aes(x = value))+
geom_density(aes(group = type, colour = type))+
coord_cartesian(xlim = c(1,100000))+
scale_color_brewer(palette="Set3")

p<-ggplot(dfs, aes(x = value))+
stat_ecdf(aes(group = type, colour = type))+
coord_cartesian(xlim = c(1,100000))+
scale_color_brewer(palette="Set3")

for (i in 1:length(args$swf_filenames)){
  p=p+annotate("text", x =14000 , y = 0.6-0.05*i, label = args$swf_filenames[i])
  p=p+annotate("text", x =40000 , y = 0.6-0.05*i, label = paste("Max: ",sprintf("%e",maxes[i])))
  p=p+annotate("text", x =60000 , y = 0.6-0.05*i, label = paste(" Mean :",sprintf("%2.0f",means[i])))
}
print (p)

###################END BLOCK#####################


#############X11 OUTPUT MANAGEMENT###############
#################MODIFY IF NEEDED################
pause_output(options_vector)
###################END BLOCK#####################


