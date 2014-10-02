#!/usr/bin/env python
# encoding: utf-8

import math
class PercentileEstimator(object):
    """Percentile estimator using the P2 algorithm as per:
    The P-squared algorithm for dynamic calculation of quantiles and histograms without storing observations,
    Raj Jain and Imrich Chlamtac
    """
    def __init__(s,p):
        s.p=p
        s.d=[0,p/2,p,(1+p)/2,1]
        s.j=0
        s.q=[0]*5

    def fit(s,x):
        if s.j<5:
            s.q[s.j]=x
            s.j+=1
        else:
            if s.j==5:
                s.q.sort()
                s.n=range(0,5)
                s.np=[0,2*s.p,4*s.p,2+2*s.p,4]

            if x<s.q[0]:
                s.q[0]=x
                k=0
            elif x<s.q[1]:
                k=0
            elif x<s.q[2]:
                k=1
            elif x<s.q[3]:
                k=2
            elif x<s.q[4]:
                k=3
            else:
                s.q[4]=x
                k=3

            for i in range(k,5):
               s.n[i]+=1
               s.np[i]+=s.d[i]


            for i in range(1,3):
                s.d[i]=s.np[i]-s.n[i]
                if (s.d[i]>=1 and s.n[i+1]-s.n[i]>1) or (s.d[i]<=-1 and s.n[i-1]-s.n[i]<-1):
                    s.d[i]=math.copysign(1,s.d[i])
                    qp=s.Psq(i)
                    if s.q[i-1]<s.q[i]<s.q[i+1]:
                        s.q[i]=qp
                    else:
                        s.q[i]=s.Lin(i)
                    s.n[i]+=s.d[i]

    def Psq(s,i):
        return s.q[i]+s.d[i]*((s.n[i]-s.n[i-1]+s.d[i])*(s.q[i+1]-s.q[i])/(s.n[i+1]-s.n[i])+(s.n[i]-s.n[i-1]+s.d[i])*(s.q[i]-s.q[i-1])/(s.n[i]-s.n[i-1]))/(s.n[i+1]-s.n[i-1])

    def Lin(s,i):
        return s.q[i]+s.d[i]*(s.q[i+int(s.d[i])]-s.q[i])/(s.n[i+int(s.d[i])]-s.n[i])


    def estimate(s):
        if s.j<5:
            s.q.sort()
            return(s.q[int(math.ceil((s.j-1)*s.p))])
        else:
            return s.q[2]

if __name__=="__main__":

    import sys
    if len(sys.argv) == 2:
        n=int(sys.argv[1])
    else:
        n=50
    from random import randint
    p=PercentileEstimator(0.95)
    l=[]
    for i in range(0,n):
        v=randint(5,300000)
        l.append(v)
        p.fit(v)
    print("P2 estimate")
    print(p.estimate())
    print("True value")
    l.sort()
    print(l[int(math.ceil((n-1)*0.9+1))])
