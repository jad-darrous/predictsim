# encoding: utf-8

class Logbarriercurve(object):
    max_loss=5000000
    def __init__(self,model,gamma):
        """slope gamma"""
        self.model=model
        self.gamma=gamma

    def d_loss_directional(self,e,x,i):
        """
           instance x
        """
        if e<self.gamma:
            return min(self.model.d_predict_directional(x, i)/(self.gamma-e),self.max_loss)
        else:
            return self.max_loss

    def grad_loss(self,e,x):
        """
        instace x
        prediction
        """
        return map(lambda i:self.model.d_predict_directional(e,x, i),range(0,len(x)))
