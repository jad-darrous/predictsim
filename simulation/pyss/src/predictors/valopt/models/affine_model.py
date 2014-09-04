# encoding: utf-8
import numpy as np

class AffineModel(object):

    def __init__(self, dim, verbose=False):
        """Linear Model, y=<w,x>"""
        self.w=np.zeros(dim+1,dtype=np.float32)
        self.dim=dim+1

    def get_param_vector(self):
        """Return a vector representation of the parameters."""
        return self.w

    def set_param_vector(self, w):
        """Set the parameter vector to a specific configuration."""
        self.w=w

    def predict(self, x):
        """Return the model prediction for an instance x"""
        return np.dot(self.w[:self.dim-1],x)+self.w[2]

    def d_predict_directional(self, x, i):
        """Return the first order directional derivative with regard to the i-th entry of the parameter vector of the model at point x"""
        if not i==self.dim-1:
            return x[i]
        else:
            return 1

    def gradient(self, x):
        """Return the gradient of the model with regard to the parameter space at point x"""
        return np.vstack((x[:self.dim-1],1))
