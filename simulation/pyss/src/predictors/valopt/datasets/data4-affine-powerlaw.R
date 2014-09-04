library("poweRlaw")
x1 = rpldis(10000,1,2)
x2 = rnorm(10000)
x3 = rnorm(10000)
z = 2*x1 + 3*x2 +8 +x3
df = data.frame(y=z,x1=x1,x2=x2)
write.table(df,quote=FALSE,file="data4-affine-powerlaw",row.names=FALSE,col.names=FALSE)
