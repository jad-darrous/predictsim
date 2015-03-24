# encoding: utf-8

class SquaredLoss(object):
    def __init__(self,model,maxloss=None):
        """Instanciate a squared loss for a specific model"""
        self.model=model

    def d_loss_directional(self,x,y,i,w=1.0,px=None):
        """Return the derivative of the loss with respect to the i-th entry of the parameter vector of the model"""
        return self.model.d_predict_directional(x, i)*(px-y)

    def grad_loss(self,x,y,w=1.0):
        """
        Gradient of the loss of the model on example (x,y)
        Should be np.array(map(lambda i:d_loss_directional(model, x, i),range(0,len(x))).
        In the case where this can be optimized, it will be different.
        """
        dif=self.model.predict(x)-y
        return [dif*self.model.d_predict_directional(x, i) for i in range(0,self.model.dim)]
