# encoding: utf-8

class Abscurve(object):
    def __init__(self,model,gamma):
        """slope gamma"""
        self.model=model
        self.gamma=float(gamma)

    def d_loss_directional(self,e,x,i):
        """
           instance x
           error e
        """
        return self.model.d_predict_directional(x, i)*self.gamma
