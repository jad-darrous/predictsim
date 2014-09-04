#!/usr/bin/env python6
# encoding: utf-8
import numpy as np

class SSGD(object):
    """
    Scaled Stochastic Gradient Descent learner with eta/n learning rate.
    Features are scaled in an online manner, using empirical mean and maximum value.
    The feature scaler is a linear transform (x-mean)/max_deviation.
    Its parameters are estimated before transformation.

    Note:
    The scaled features are, to the best of our abilities of mean 0 and between -1 and 1.
    There is however no guarantee on their variance.
    """

    def __init__(self, model, loss, eta, verbose=False,scaler="scale_mean0"):
        self.model=model
        self.loss=loss
        self.grad_loss=lambda x,y:self.loss.grad_loss(x,y)
        self.eta=eta
        self.verbose=verbose
        self.n=1
        if scaler=="scale_mean0":
            self.scalersum=np.zeros(model.dim)
            self.scalermaxes=np.zeros(model.dim)
            self.scale=self.scale_mean0
        elif scaler=="scale_rescale01":
            self.scalermaxes=np.zeros(model.dim)
            self.scalermins=np.zeros(model.dim)
            self.scale=self.scale_rescale01
        elif scaler=="scale_unitlength":
            self.scale=self.scale_unitlength
        elif scaler=="scale_standardize11":
            self.scale=self.scale_standardize11
            self.scalermean=np.zeros(model.dim)
            self.scalerstd=np.zeros(model.dim)
            self.scalerM2=np.zeros(model.dim)
        else:
            raise ValueError("No valid scaler specified to the SSGD.")

    def predict(self, x):
        return self.model.predict(self.scale(x))

    def verbose(func):
         def wrap(self,x,y):
             if self.verbose:
                 print(self.model.get_param_vector())
                 print(self.eta*self.grad_loss(x,y))
             ret = func(self,x,y)
             if self.verbose:
                 print("gradient descent step with fixed eta: gradient l2 norm is %s"
                         %(-self.eta*np.dot(self.grad_loss(x,y),self.grad_loss(x,y))))
             return ret
         return wrap

    @verbose
    def fit(self, x,y):
        x_scaled=self.scale(x,update=True)
        self.model.set_param_vector(self.model.get_param_vector()-(self.eta*self.grad_loss(x_scaled,y)/self.n))
        self.n+=1

    def scale_mean0(self, x,update=False):
        """
        Features are scaled in an online manner, using empirical mean and maximum value.
        The feature scaler is a linear transform (x-mean)/max_deviation.
        Its parameters are estimated before transformation.

        Note:
        The scaled features are, -to the best of our abilities in this constrained online setting-
        of mean 0 and between -1 and 1.
        There is however no guarantee on their variance.

        This performs poorly in general for SGD.
        """
        if update:
            self.scalermaxes=np.maximum(self.scalermaxes,np.abs(x))
            self.scalersum=self.scalersum+x

        if self.n==1:
            return np.zeros(self.model.dim)
        else:
            return np.divide(x-(self.scalersum/(self.n)),self.scalermaxes)

    def scale_rescale01(self,x,update=False):
        """
        Feature rescaling to [0,1] using x'=(x-min)/(max-min)

        This performs poorly in general for SGD.
        """
        if update:
            self.scalermaxes=np.maximum(self.scalermaxes,x)
            self.scalermins=np.minimum(self.scalermins,x)

        if self.n==1:
            return np.zeros(self.model.dim)
        else:
            return np.divide(x-self.scalermins,self.scalermaxes-self.scalermins)

    def scale_unitlength(self, x,update=False):
        """
        Scales x to be of unit length according to l2 norm.

        This performs well but not great for SGD.
        The method fails to accomodate powerlaw-distributed features.
        """
        return x/np.linalg.norm(x)

    def scale_standardize11(self, x,update=False):
        """
        Online standardization of values to mean 0 and variance 1.
        Variance is computed online using the algorithm from Knuth/Welford:
        http://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Incremental_algorithm
        """

        if update:
            delta = x - self.scalermean
            self.scalermean = self.scalermean + delta/self.n
            self.scalerM2 = self.scalerM2 + delta*(x - self.scalermean)

        if (self.n < 2):
            return np.zeros(self.model.dim)
        else:
            variance = self.scalerM2/(self.n - 1)
            return np.divide(x-self.scalermean,np.sqrt(variance))
