# encoding: utf-8

class L2(object):

    def norm(self,w):
        return 0.5*sum([e*e for e in w])

    def d_norm_directional(self,w,i):
        return w[i]

    def grad_norm(self,w):
        return w
