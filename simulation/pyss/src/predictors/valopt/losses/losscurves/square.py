# encoding: utf-8

class Squarecurve(object):
    def __init__(self,model,gamma):
        """slope gamma"""
        self.model=model
        self.gamma=gamma

    def d_loss_directional(self,e,x,i):
        """
           instance x
           error e
        """
        return self.gamma*2*self.model.d_predict_directional(x, i)*e

    def grad_loss(self,e,x):
        """
        instace x
        prediction
        """
        return map(lambda i:self.model.d_predict_directional(e,x, i),range(0,len(x)))
