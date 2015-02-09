#!/usr/bin/env python3
# encoding: utf-8

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
        self.s=[0]*model.dim
        self.N=0

    def predict(self, x):
        return self.model.predict(x)

    def fit(self, x,y,w=1):
        W=self.model.get_param_vector()
        for i in range(0,self.model.dim):
            if abs(x[i])>self.s[i]:
                W[i]=W[i]*self.s[i]*self.s[i]/(x[i]*x[i])
                self.s[i]=abs(x[i])
        self.N=self.N+(sum([e**2 for e in x])/(self.s**2))

        G=self.loss.d_loss_directional(x,y,i,w)
        for i in range(0,self.model.dim):
            W[i]-= self.eta*self.n*self.loss.d_loss_directional(x,y,i)/(self.N*self.s[i]*self.s[i])

        self.n+=1
