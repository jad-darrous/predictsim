#!/usr/bin/env python3
# encoding: utf-8
import numpy as np

class SGD(object):
    """Stochastic Gradient Descent learner with eta/n learning rate"""

    def __init__(self, model, loss, eta, verbose=False):
        self.model=model
        self.loss=loss
        self.grad_loss=lambda x,y:self.loss.grad_loss(x,y)
        self.eta=eta
        self.verbose=verbose
        self.n=1

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
        self.model.set_param_vector(self.model.get_param_vector()-(self.eta*self.grad_loss(x,y)/self.n))
        self.n+=1
