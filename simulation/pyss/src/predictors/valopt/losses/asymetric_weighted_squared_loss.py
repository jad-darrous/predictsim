# encoding: utf-8
import numpy as np

class AsymetricWeightedSquaredLoss(object):
    def __init__(self,model,beta):
        """
        Instanciate an asymetric weighted squared loss for a specific model.
        beta: scaling factor to positive error/negative error (prediction>true value)loss ratio to (true value>prediction) weighting.
        beta should be high if the model is to be fit as to favor under-estimating the true value.
        """
        self.model=model
        self.beta=beta

    def loss(self,x,y,w):
        """Return the squared loss of the model on example (x,y) with weight p"""
        p=self.model.predict(x)
        r=0.5*(p-y)*(p-y)*w
        return r*self.beta if p>y else r

    def d_loss_directional(self,x,y,i,w):
        """Return the derivative of the loss with respect to the i-th entry of the parameter vector of the model"""
        p=self.model.predict(x)
        r=self.model.d_predict_directional(x, i)*(p-y)*w
        return r*self.beta if p>y else r

    def grad_loss(self,x,y,w):
        """
        Gradient of the loss of the model on example (x,y)
        Should be np.array(map(lambda i:d_loss_directional(model, x, i),range(0,len(x))).
        In the case where this can be optimized, it will be different.
        """
        p=self.model.predict(x)
        r=(p-y)*np.array(map(lambda i:self.model.d_predict_directional(x, i),range(0,self.model.dim)))*w
        return r*self.beta if p>y else r
