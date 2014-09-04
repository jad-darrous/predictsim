x1 = rnorm(10000)
x2 = rnorm(10000)
z = 2*x1 + 3*x2
df = data.frame(y=z,x1=x1,x2=x2)
write.table(df,quote=FALSE,file="data1-linear",row.names=FALSE,col.names=FALSE)
