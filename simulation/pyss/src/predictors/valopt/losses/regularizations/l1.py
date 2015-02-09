# encoding: utf-8

class L1(object):

    def norm(self,w):
        return sum([abs(e) for e in w])

    def d_norm_directional(self,w,i):
        if w[i]>0:
            return 1
        elif w[i]==0:
            return 0
        else:
            return -1

    def grad_norm(self,w):
        return [self.d_norm_directional(w, i) for i in range(0,len(w))]
