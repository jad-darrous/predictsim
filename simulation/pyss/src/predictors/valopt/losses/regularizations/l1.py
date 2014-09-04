# encoding: utf-8
import numpy as np
from numpy import linalg as la

class L1(object):

    def norm(self,w):
        return la.norm(w,1)

    def d_norm_directional(self,w,i):
        return 1 if w[i]>=0 else -1

    def grad_norm(self,w):
        return np.array(map(lambda i:self.d_norm_directional(w, i),range(0,len(w))))
