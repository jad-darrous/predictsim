#!/usr/bin/env python3
# encoding: utf-8
import math

class NAG(object):
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

    #def verbose(func):
         #def wrap(self,x,y,p):
             #if self.verbose:
                 #print(self.model.get_param_vector())
                 #print(self.eta*self.grad_loss(x,y,p))
             #ret = func(self,x,y)
             #if self.verbose:
                 #print("gradient descent step with fixed eta: gradient l2 norm is %s"
                         #%(-self.eta*np.dot(self.grad_loss(x,y,p),self.grad_loss(x,y,p))))
             #return ret
         #return wrap

    #@verbose
    def fit(self, x,y,w=1):
        W=self.model.get_param_vector()
        for i in range(0,self.model.dim):
            if abs(x[i])>self.s[i]:
                W[i]*=self.s[i]/abs(x[i])
                self.s[i]=abs(x[i])

        #for i in range(0,self.model.dim):
            #if self.s[i]==0:
                #self.s[i]=0.01

        self.N=self.N+sum([a*a/(b*b) for a,b in zip(x,self.s) if not b==0])

        self.model.set_param_vector(W)

        for i in range(0,self.model.dim):
            self.G[i]+= (self.loss.d_loss_directional(x,y,i,w))**2
            if not self.G[i]==0:
                W[i]-= self.eta*self.loss.d_loss_directional(x,y,i,w)/(math.sqrt(self.N*self.G[i]/self.n)*self.s[i])

        self.n+=1
        self.model.set_param_vector(W)
