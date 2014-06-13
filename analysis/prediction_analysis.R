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

df <- read.table(args$filename)
names(df) <- c('true_run','tsafir','random_forest')
#df$true_run=as.numeric(as.character(df$true_run))
#df$col1=as.numeric(as.character(df$col1))
#df$col2=as.numeric(as.character(df$col2))
#summary(df)
#print(df$col1[1])
#print(df$true_run[1])

#print(sum(df$true_run**2))
N=length(df$true_run)
print((1/N)*sum((df$true_run-df$tsafir)^2))
print((1/N)*sum((df$true_run-df$random_forest)^2))


t=df$true_run-df$tsafir
r=df$true_run-df$random_forest



t_abs=abs(t)
r_abs=abs(r)
print("mean tsaf")
print(mean(t_abs))
print("mean rf")
print(mean(r_abs))
print("var tsaf")
print(sqrt(var(t_abs)/length(r_abs)))
print("var rf")
print(sqrt(var(r_abs)/length(r_abs)))

t_sq=t^2
r_sq=r^2
t_ssq=sign(t)*t_sq
r_ssq=sign(r)*r_sq
l=length(t)
values=c(t_abs,r_abs)
belongs=c(rep("baseline",l),rep("randomforest",l))
df <-data.frame(values,belongs)
colnames(df) <- c("value", "type")
summary(df)

print("dbg")
library(ggplot2)
#ggplot(df, aes(x=value)) +geom_histogram(aes(y=..density..),alpha=0.2) +geom_density(fill=NA,alpha=0.2)
m <- ggplot(df, aes(x=value))
m +
geom_density(aes(group=type,fill=type),adjust=4, colour="black",alpha=0.2,fill="gray20")+
coord_trans(y = "sqrt")+
scale_x_continuous(breaks=seq(from=0,to=86400,by=3600),labels=seq(from=0,to=24,by=1))+
xlab("Absolute error (hours)")+
ylab("Density")+
ggtitle("Kernel density estimation of the absolute error.")+
annotate("text",x=12500,y=0.000025,label="Random Forest",size=5)+
annotate("text",x=4500,y=0.0003,label="Baseline",size=5)+
theme_bw()



#m + geom_histogram(aes(y=..density..,fill=type),binwidth=1800) + geom_density(aes(fill=type, y = ..scaled..), colour="black",alpha=0.2)
#ggplot(df, aes(x=value)) +geom_histogram(aes(fill=type,y=..density..),alpha=0.2,position="dodge") +geom_density(aes(fill=type),kernel="rectangular",alpha=0.2)
#ggplot(df, aes(x=value,y=..density..)) +geom_histogram(aes(fill=type),alpha=0.2,position="dodge") +geom_density(aes(fill=type),kernel="rectangular",alpha=0.2)

#ggplot(df, aes(value)) +geom_density(aes(fill=type),kernel="rectangular")


#ggplot(df, aes(x=type,y=value)) +geom_boxplot()





###################END BLOCK#####################


#############X11 OUTPUT MANAGEMENT###############
#################MODIFY IF NEEDED################
pause_output(options_vector)
###################END BLOCK#####################


