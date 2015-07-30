
import os
import sys
import datetime
import time


from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model

import numpy as np
from sklearn.svm import SVR
from matplotlib import pyplot as plt
from sklearn.datasets import  load_boston
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import regression
from itertools import izip


from math import sin, cos


def accuracy(actual, pred):
    x1 = sum(1 if u>v else 0 for u,v in izip(actual, pred))
#     X = map(lambda u: u[1], s)
#     y = map(lambda u: u[0], s)
    x2 = sum(1 if u<v else 0 for u,v in izip(actual, pred))
    x3 = sum(1 if u==v else 0 for u,v in izip(actual, pred))
    t1 = max(v-u if u<v else 0 for u,v in izip(actual, pred))
    t2 = max(u-v if u>v else 0 for u,v in izip(actual, pred))
    print " + Under/Over/Exact estimation:", x1, x2, x3
    print " + Min/Max Under/Over estimation:", int(t1), int(t2)


# for fname in ["times-epp-tsr.txt", "times-epp-sgd.txt", "times-epp-req.txt", "times-epp-dbl-req.txt"]:
#     s = []
#     for line in open(fname):
#         s.append(map(float, line.split()))
#     print regression.mean_squared_error(X, y), fname
#     accuracy(y, X)



def build_predictor(fname):

    s = []
    d1, d2 = 0, 0
    for line in open(fname):
        s.append(map(float, line.split()))
    # s = s[5000:]

    # print '--- Error on complete set'
    # y = map(lambda u: u[0], s)
    # for idx, val in enumerate(["reqtime", "tsafrir", "sgd"]):
    #     xi = map(lambda u: u[idx+1], s)
    #     print regression.mean_squared_error(y, xi), val
    #     accuracy(y, xi)

    # s = []
    # for i in range(-100,100,3):
    #     # s.append([7*(i**3)-5*i*i-17*i+8, i,i*i,i*i*i])
    #     s.append([7*(i**3)-5*i*i-17*i+8, i])

    import random
    random.shuffle(s)

    # s=[ [1, 6,8,9], [5, 6,8,9], [7, 6,8,9], [2, 7,8,9]]

    # keyfunc = lambda u: u[0]
    # s.sort(key=keyfunc)

    print "original data size", len(s)

    # mp = {}
    # for r in s:
    #     key, val = r[0], r[1:]
    #     if not key in mp:
    #         mp[key] = []
    #     mp[key].append(val)

    # s = []
    # for key in mp:
    #     l = mp[key]
    #     if len (l) > 1:
    #         t = reduce(lambda u,v: [i+j for i,j in izip(u,v)], l)
    #         t = map(lambda u: 1.0*u/len(l), t)
    #         mp[key] = t
    #     else:
    #         mp[key] = l[0]
    #     s.append([key] + mp[key])

    # print "data size later", len(s)

    mp = {}
    for r in s:
        key, val = r[0], tuple(r[1:])
        if not val in mp:
            mp[val] = []
        mp[val].append(key)

    s = []
    for key in mp:
        l = mp[key]
        mp[key] = sum(l)/len(l)
        s.append([mp[key]] + list(key))

    print "data size later", len(s)

    X = map(lambda u: u[1:], s)
    # X = map(lambda u: [u[1]], s)
    y = map(lambda u: u[0], s)

    # print len(X), len(set(tuple(u) for u in X))

    import itertools

    for x in X:
        t = []
        for i in x:
            t.extend([i*i,i**3])
        for a,b in itertools.combinations(x, 2):
            t.append(a*b)
        for a,b,c in itertools.combinations(x, 3):
            t.append(a*b*c)
        x.extend(t)


    # prepare the training and testing data for the model
    nCases = len(y)
    nTrain = int(np.floor(nCases * 0.8))
    trainX = X[:nTrain]
    trainY = y[:nTrain]
    testX = X[nTrain:]
    testY = y[nTrain:]


    # print type(X), X[0]
    svr = SVR(kernel='linear', C=1.0, epsilon=0.2)
    svr = SVR(kernel='rbf', C=1.0, epsilon=0.2, gamma=.0001)
    log = LinearRegression(normalize=True)

    # train both models
    # svr.fit(trainX, trainY)
    log.fit(trainX, trainY)

    # predict test labels from both models
    predLog = log.predict(testX)
    # predSvr = svr.predict(testX)

    # show it on the plot
    # plt.plot(testY, testY, label='true data')
    # # plt.plot(testY, predSvr, 'co', label='SVR')
    # plt.plot(testY, predLog, 'mo', label='LogReg')
    # plt.legend()
    # plt.show()


    print '--- Error on test set'
    meta_mse = regression.mean_squared_error(testY, predLog)
    print int(meta_mse), "meta predictor"
    # print regression.mean_squared_error(testY, predSvr)

    well_estimated = sum([1 if abs(u-v)<2*u else 0 for u,v in izip(testY, predLog)])
    print "well estimated, all, percent: ", well_estimated, len(testY), int(100.0*well_estimated/len(testY)), "%"
    exit(0)

    for idx, val in enumerate(["reqtime", "tsafrir", "sgd"]):
        mse = regression.mean_squared_error(testY, map(lambda u: u[idx], testX))
        print "%d %.2f %% %s" % (mse, 100*(mse-meta_mse)/mse, val)
        # print mse, int(100*(mse-meta_mse)/mse), "%", val


build_predictor("times.txt")

