n=100000
x1 = rpareto(n,0,1)
ind = which(x1 > 10000)
x1[ind] <- 10000
x2 = rnorm(n)
x3 = rnorm(n)
z = 2*x1 + 3*x2 +x3
df = data.frame(y=z,x1=x1,x2=x2)
write.table(df,quote=FALSE,file="data5-linear-powerlaw",row.names=FALSE,col.names=FALSE)
