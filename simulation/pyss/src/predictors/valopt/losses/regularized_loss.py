# encoding: utf-8

class RegularizedLoss(object):
    def __init__(self,model,orig_loss,regularizer,alpha):
        """Instanciate a regularized loss given a normal loss"""
        self.model=model
        self.orig_loss=orig_loss
        self.regularizer=regularizer
        self.alpha=alpha

    def loss(self,x,y,w=1):
        """Return the squared loss of the model on example (x,y)"""
        return self.orig_loss.loss(x,y,w=w)+self.alpha*self.regularizer.norm(self.model.get_param_vector())

    def d_loss_directional(self,x,y,i,w=1):
        """Return the derivative of the loss with respect to the i-th entry of the parameter vector of the model"""
        return self.orig_loss.d_loss_directional(x,y,i,w=w)+self.alpha*self.regularizer.d_norm_directional(self.model.get_param_vector(),i)

    def grad_loss(self,x,y,w=1):
        """Gradient of the loss of the model on example (x,y) """
        G=self.orig_loss.grad_loss(x,y,w=w)
        R=self.regularizer.grad_norm(self.model.get_param_vector())
        l=self.model.dim*[0]
        for i in range(0,self.model.dim):
            l[i]=G[i]+self.alpha*R[i]
        return l
