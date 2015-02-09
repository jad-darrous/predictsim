# encoding: utf-8
#import copy

class LinearModel(object):

    def __init__(self, dim, verbose=False):
        """Linear Model, y=<w,x>"""
        self.w=[0]*dim
        self.dim=dim

    def get_param_vector(self):
        """Return a vector representation of the parameters."""
        #return copy.deepcopy(self.w)
        return self.w

    def set_param_vector(self, w):
        """Set the parameter vector to a specific configuration."""
        self.w=w

    def predict(self, x):
        """Return the model prediction for an instance x"""
        r=0
        for i in range(0,self.dim):
            r+=self.w[i]*x[i]
        return r

    def d_predict_directional(self, x, i):
        """Return the first order directional derivative with regard to the i-th entry of the parameter vector of the model at point x"""
        return x[i]

    def gradient(self, x):
        """Return the gradient of the model with regard to the parameter space at point x"""
        return x
