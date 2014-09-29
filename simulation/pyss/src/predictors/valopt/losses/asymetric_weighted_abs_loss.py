# encoding: utf-8

class AsymetricWeightedAbsLoss(object):
    def __init__(self,model,beta,gamma):
        """
        Instanciate an asymetric weighted squared loss for a specific model.
        beta: scaling factor to positive error/negative error (prediction>true value)loss ratio to (true value>prediction) weighting.
        beta should be high if the model is to be fit as to favor under-estimating the true value.
        """
        self.model=model
        self.beta=beta
        self.gamma=gamma

    def loss(self,x,y,w):
        """Return the squared loss of the model on example (x,y) with weight p"""
        p=self.model.predict(x)
        r=abs((p-y)*w)
        return r*self.beta if p>y else r*self.gamma

    def d_loss_directional(self,x,y,i,w):
        """Return the derivative of the loss with respect to the i-th entry of the parameter vector of the model"""
        p=self.model.predict(x)
        if (p-y)>=0:
            return self.model.d_predict_directional(x, i)*w*self.beta
        else:
            return -self.model.d_predict_directional(x, i)*w*self.gamma

    def grad_loss(self,x,y,w):
        """
        Gradient of the loss of the model on example (x,y)
        Should be np.array(map(lambda i:d_loss_directional(model, x, i),range(0,len(x))).
        In the case where this can be optimized, it will be different.
        """
        if (self.model.predict(x)-y)>=0:
            return map(lambda i:self.model.d_predict_directional(x, i),range(0,len(x)))*w*self.beta
        else:
            return map(lambda i:-self.model.d_predict_directional(x, i),range(0,len(x)))*w*self.gamma
