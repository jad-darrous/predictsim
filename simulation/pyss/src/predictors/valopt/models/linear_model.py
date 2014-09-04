# encoding: utf-8
import numpy as np

class LinearModel(object):

    def __init__(self, dim, verbose=False):
        """Linear Model, y=<w,x>"""
        self.w=np.zeros(dim,dtype=np.float32)
        self.dim=dim

    def get_param_vector(self):
        """Return a vector representation of the parameters."""
        return self.w

    def set_param_vector(self, w):
        """Set the parameter vector to a specific configuration."""
        self.w=w

    def predict(self, x):
        """Return the model prediction for an instance x"""
        return np.dot(self.w,x)

    def d_predict_directional(self, x, i):
        """Return the first order directional derivative with regard to the i-th entry of the parameter vector of the model at point x"""
        return x[i]

    def gradient(self, x):
        """Return the gradient of the model with regard to the parameter space at point x"""
        return x
