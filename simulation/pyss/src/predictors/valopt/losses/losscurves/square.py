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
