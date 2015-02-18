# encoding: utf-8

class CompositeLoss(object):
    def __init__(self,model,rightside,leftside,threshold):
        """Instanciate a squared loss for a specific model"""
        self.model=model
        self.rightside=rightside
        self.leftside=leftside
        self.threshold=threshold

    #def loss(self,x,y,w=1):
        #"""Return the squared loss of the model on example (x,y)"""
        #p=self.model.predict(x)
        #if p-y>self.threshold:
            #return w*self.rightside.loss(p-y-self.threshold)
        #elif p-y==self.threshold:
            #return 0
        #else:
            #return -w*self.rightside.loss(self.threshold-p+y)

    def d_loss_directional(self,x,y,i,w=1):
        """Return the derivative of the loss with respect to the i-th entry of the parameter vector of the model"""
        p=self.model.predict(x)
        if p-y>self.threshold:
            return w*self.rightside.d_loss_directional(p-y-self.threshold,x,i)
        elif p-y==self.threshold:
            return 0
        else:
            return -w*self.rightside.d_loss_directional(self.threshold-p+y,x,i)

    def grad_loss(self,x,y,w=1):
        """
        Gradient of the loss of the model on example (x,y)
        Should be np.array(map(lambda i:d_loss_directional(model, x, i),range(0,len(x))).
        In the case where this can be optimized, it will be different.
        """
        return [self.d_loss_directional(x, y,i, w) for i in range(0,self.model.dim)]
