x1 = rnorm(10000)
x2 = rnorm(10000)
x3 = rnorm(10000)
z = 2*x1 + 3*x2 +x3
df = data.frame(y=z,x1=x1,x2=x2)
write.table(df,quote=FALSE,file="data3-linear-perturbed",row.names=FALSE,col.names=FALSE)
