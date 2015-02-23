# encoding: utf-8
import math

class Expcurve(object):
    max_loss=5000000
    def __init__(self,model,gamma):
        """slope gamma"""
        self.model=model
        self.gamma=gamma

    def d_loss_directional(self,e,x,i):
        """
           instance x
        """
        return self.gamma*self.model.d_predict_directional(x, i)*math.exp(self.gamma*e)
