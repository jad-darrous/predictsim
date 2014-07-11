##########################################################
# Exploratory graphs for Campaign Scheduling evaluation
# Author: Vinicius Pinheiro
##########################################################



vinicius_compare_parametrized <-function(fileOri,fileNew,treshold){

stretchOri <- read.csv(fileOri, header=FALSE, sep=" ")
stretchNew <- read.csv(fileNew, header=FALSE, sep=" ")

stretchOri<- stretchOri[stretchOri$V2 < treshold,]
stretchNew<- stretchNew[stretchNew$V2 < treshold,]

# Generating scatter plots
plot(stretchOri$V1 ~ stretchOri$V2,main="scatter plot of stretchs by campaign.", col="green", pch=19)
plot(stretchNew$V1 ~ stretchNew$V2, col="blue", pch=19)

# Histograms.
hist(stretchOri$V2,col="green", breaks=100)
hist(stretchNew$V2,col="blue", breaks=100)

# Density plots
plot(density(stretchOri$V2),col="green", lwd=3)
lines(density(stretchNew$V2),col="blue", lwd=3)

# Generating smooth scatter plots
smoothScatter(stretchOri$V2, stretchOri$V1)
smoothScatter(stretchNew$V2, stretchNew$V1)


}	


vinicius_compare<-function(fileOri,fileNew){
# Loading files
stretchOri <- read.csv(fileOri, header=FALSE, sep=" ")
stretchNew <- read.csv(fileNew, header=FALSE, sep=" ")

# Filtering intervals
stretchOri1000 <- stretchOri[stretchOri$V2 < 1000,]
stretchOri100 <- stretchOri[stretchOri$V2 < 100,]
stretchOri10 <- stretchOri[stretchOri$V2 < 10,]

stretchNew1000 <- stretchNew[stretchNew$V2 < 1000,]
stretchNew100 <- stretchNew[stretchNew$V2 < 100,]
stretchNew10 <- stretchNew[stretchNew$V2 < 10,]

par(mfrow=c(2,2))
# Generating scatter plots
plot(stretchOri$V1 ~ stretchOri$V2, col="green", pch=19)
plot(stretchNew$V1 ~ stretchNew$V2, col="blue", pch=19)

plot(stretchOri1000$V1 ~ stretchOri1000$V2, col="green", pch=19)
plot(stretchNew1000$V1 ~ stretchNew1000$V2, col="blue", pch=19)

plot(stretchOri100$V1 ~ stretchOri100$V2, col="green", pch=19)
plot(stretchNew100$V1 ~ stretchNew100$V2, col="blue", pch=19)

plot(stretchOri10$V1 ~ stretchOri10$V2, col="green", pch=19)
plot(stretchNew10$V1 ~ stretchNew10$V2, col="blue", pch=19)

# Generating histrograms

hist(stretchOri$V2,col="green", breaks=100)
hist(stretchNew$V2,col="blue", breaks=100)

hist(stretchOri1000$V2,col="green", breaks=100)
hist(stretchNew1000$V2,col="blue", breaks=100)

hist(stretchOri100$V2,col="green", breaks=100)
hist(stretchNew100$V2,col="blue", breaks=100)

hist(stretchOri10$V2,col="green", breaks=100)
hist(stretchNew10$V2,col="blue", breaks=100)

# Generating density plots

plot(density(stretchOri$V2),col="green", lwd=3)
lines(density(stretchNew$V2),col="blue", lwd=3)

plot(density(stretchOri1000$V2),col="green", lwd=3)
lines(density(stretchNew1000$V2),col="blue", lwd=3)

plot(density(stretchOri100$V2),col="green", lwd=3)
lines(density(stretchNew100$V2),col="blue", lwd=3)

plot(density(stretchOri10$V2),col="green", lwd=3)
lines(density(stretchNew10$V2),col="blue", lwd=3)

# Generating smooth scatter plots

smoothScatter(stretchOri$V2, stretchOri$V1)
smoothScatter(stretchNew$V2, stretchNew$V1)

smoothScatter(stretchOri1000$V2, stretchOri1000$V1)
smoothScatter(stretchNew1000$V2, stretchNew1000$V1)

smoothScatter(stretchOri100$V2, stretchOri100$V1)
smoothScatter(stretchNew100$V2, stretchNew100$V1)

smoothScatter(stretchOri10$V2, stretchOri10$V1)
smoothScatter(stretchNew10$V2, stretchNew10$V1)
}
