#!/usr/bin/env python3
# encoding: utf-8
#import numpy as np

class SGD(object):
    """Stochastic Gradient Descent learner with eta/n learning rate"""

    def __init__(self, model, loss, eta, verbose=False):
        self.model=model
        self.loss=loss
        self.eta=eta
        self.verbose=verbose
        self.n=200

    def predict(self, x):
        #print(self.model.get_param_vector())
        return self.model.predict(x)

    def fit(self, x,y,w=1):
        W=self.model.get_param_vector()
        G=self.loss.grad_loss(x,y,w)
        print(G)
        for i in range(0,self.model.dim):
            W[i]-=self.eta*0.00000000001*G[i]/float(self.n)
        self.n+=1
        self.model.set_param_vector(W)
