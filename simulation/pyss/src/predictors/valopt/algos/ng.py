#!/usr/bin/env python3
# encoding: utf-8
import numpy as np

class NG(object):
    """
    Normalized Gradient Descent learner.
    As per Ross,Mineiro,Langford: "Normalized Online Learning" (UAI2013)
    Works only with LinearModel
    """

    def __init__(self, model, loss, eta, verbose=False):
        self.model=model
        assert model.__class__.__name__=='LinearModel'
        self.loss=loss
        self.grad_loss=lambda x,y:self.loss.grad_loss(x,y)
        self.eta=eta
        self.verbose=verbose
        self.n=1
        self.s=np.zeros(model.dim)
        self.N=0

    def predict(self, x):
        return self.model.predict(x)

    def verbose(func):
         def wrap(self,x,y):
             if self.verbose:
                 print(self.model.get_param_vector())
                 print(self.eta*self.grad_loss(x,y))
             ret = func(self,x,y)
             if self.verbose:
                 print("gradient descent step with fixed eta: gradient l2 norm is %s"
                         %(-self.eta*np.dot(self.grad_loss(x,y),self.grad_loss(x,y))))
             return ret
         return wrap

    @verbose
    def fit(self, x,y):
        w=self.model.get_param_vector()
        for i in range(0,self.model.dim):
            if np.abs(x[i])>self.s[i]:
                w[i]=w[i]*self.s[i]*self.s[i]/(x[i]*x[i])
                self.s[i]=np.abs(x[i])
        self.N=self.N+np.sum(x*x/(self.s*self.s))
        self.model.set_param_vector(w)
        G=self.loss.d_loss_directional(x,y,i)

        for i in range(0,self.model.dim):
            w[i]=w[i] - self.eta*self.n*self.loss.d_loss_directional(x,y,i)/(self.N*self.s[i]*self.s[i])
        self.n+=1

        self.model.set_param_vector(w)
