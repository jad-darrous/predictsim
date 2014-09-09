# encoding: utf-8
import numpy as np

class AbsLoss(object):
    def __init__(self,model):
        """Instanciate an absolute loss for a specific model"""
        self.model=model

    def loss(self,x,y,w=1):
        """Return the absolute loss of the model on example (x,y)"""
        return np.abs(self.model.predict(x)-y)

    def d_loss_directional(self,x,y,i,w=1):
        """Return the derivative of the loss with respect to the i-th entry of the parameter vector of the model"""
        if np.sign(self.model.predict(x)-y)==1:
            return self.model.d_predict_directional(x, i)
        else:
            return -self.model.d_predict_directional(x, i)

    def grad_loss(self,x,y,w=1):
        """
        Gradient of the loss of the model on example (x,y)
        Should be np.array(map(lambda i:d_loss_directional(model, x, i),range(0,len(x))).
        In the case where this can be optimized, it will be different.
        """
        if np.sign(self.model.predict(x)-y)==1:
            return np.array(map(lambda i:self.model.d_predict_directional(x, i),range(0,len(x))))
        else:
            return np.array(map(lambda i:-self.model.d_predict_directional(x, i),range(0,len(x))))
