# encoding: utf-8
import numpy as np
from numpy import linalg as la

class L2(object):

    def norm(self,w):
        return 0.5*np.dot(w,w)

    def d_norm_directional(self,w,i):
        return w[i]

    def grad_norm(self,w):
        return w
