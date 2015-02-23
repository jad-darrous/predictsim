#!/usr/bin/env python3
# encoding: utf-8
import math
#import copy

class sNAG(object):
    """
    Normalized Adaptive Gradient Descent learner.
    As per Ross,Mineiro,Langford: "Normalized Online Learning" (UAI2013)
    Works only with LinearModel
    """

    def __init__(self, model, loss, eta, verbose=False):
        self.model=model
        assert model.__class__.__name__=='LinearModel'
        self.loss=loss
        self.grad_loss=lambda x,y,p:self.loss.grad_loss(x,y,p)
        self.eta=eta
        self.verbose=verbose
        self.n=1
        self.s=[0]*model.dim
        self.G=[0]*model.dim
        self.N=0

    def predict(self, x):
        return self.model.predict(x)

    def fit(self, x,y,w=1):
        W=self.model.get_param_vector()
        #print("N: %s" %self.N)
        #print("G: %s" %self.G)
        #print("W: %s" %W)
        for i in range(0,self.model.dim):
            self.s[i]+=x[i]*x[i]
            #if abs(x[i])>math.sqrt(self.s[i]/self.n):
                #W[i]*=math.sqrt(self.s[i])/(abs(x[i])*math.sqrt(self.n))

        self.model.set_param_vector(W)
        self.N=self.N+sum([xi*xi/(si*si) for xi,si in zip(x,self.s) if not si==0])

        l=[0]*self.model.dim
        for i in range(0,self.model.dim):
            self.G[i]+= (self.loss.d_loss_directional(x,y,i,w))**2
            if not self.G[i]==0:
                l[i]= -self.eta*self.n*self.loss.d_loss_directional(x,y,i,w)/math.sqrt(self.N*self.G[i]*self.s[i])
        W=[a+b for a,b in zip(l,W)]
        self.model.set_param_vector(W)

        self.n+=1
