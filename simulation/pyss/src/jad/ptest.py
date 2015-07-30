
import os
import sys
import datetime
import time
from swf_utils import *

import multiprocessing
import time

import sys
sys.path.append("..")


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


for f in os.listdir("logs/"):
    if not f == "new":
        classify_jobs("logs/" + f)

exit(0)


# # y_true = [3, -0.5, 2, 7, -99, 532, 0]
# # y_pred = [2.5, 0.0, 2, 8, 7, 157, 751]
# # print regression.mean_squared_error(y_true, y_pred)

# # print sum(map(lambda u: (u[0]-u[1])**2, izip(y_true, y_pred)))/len(y_true)
# # exit(0)

# for fname in ["times-epp.txt", "times-epp-sgd.txt"]:
#     s = []
#     for line in open(fname):
#         s.append(map(float, line.split()))
#     X = map(lambda u: u[1], s)
#     y = map(lambda u: u[0], s)
#     print regression.mean_squared_error(X, y), fname


# if 0:
#     # data = load_diabetes()
#     data = load_boston()
#     X = data.data
#     y = data.target
# else:
#     s = []
#     d1, d2 = 0, 0
#     for line in open("times.txt"):
#         s.append(map(float, line.split()))
#     # s = s[5000:]

#     y = map(lambda u: u[0], s)
#     for idx, val in enumerate(["reqtime", "tsafrir", "sgd"]):
#         print regression.mean_squared_error(y, map(lambda u: u[idx+1], s)), val


#     import random
#     random.shuffle(s)

#     X = map(lambda u: u[1:], s)
#     # X = map(lambda u: [u[1]], s)
#     y = map(lambda u: u[0], s)


# # prepare the training and testing data for the model
# nCases = len(y)
# nTrain = int(np.floor(nCases * 0.4))
# trainX = X[:nTrain]
# trainY = y[:nTrain]
# testX  = X[nTrain:]
# testY = y[nTrain:]

# # print type(X), X[0]
# svr = SVR(kernel='linear', C=1.0, epsilon=0.2)
# svr = SVR(kernel='rbf', C=1.0, epsilon=0.2, gamma=.0001)
# log = LinearRegression()

# # train both models
# # svr.fit(trainX, trainY)
# log.fit(trainX, trainY)

# # predict test labels from both models
# predLog = log.predict(testX)
# # predSvr = svr.predict(testX)

# # show it on the plot
# # plt.plot(testY, testY, label='true data')
# # plt.plot(testY, predSvr, 'co', label='SVR')
# # plt.plot(testY, predLog, 'mo', label='LogReg')
# # plt.legend()
# # plt.show()

# print testX
# print svr.predict(testX)
# # print regression.mean_squared_error(testY, predLog)
# # # print regression.mean_squared_error(testY, predSvr)

# # print regression.mean_squared_error(testY, map(lambda u: u[0], testX))
# # print regression.mean_squared_error(testY, map(lambda u: u[1], testX))

# exit(0)

# s = []
# for line in open("times.txt"):
#     s.append(map(float, line.split()))
# s = s[5000:]

# l = len(s)*2/3
# train, test = s[:l], s[l:]
# X = map(lambda u: u[1:], train)
# vector = map(lambda u: u[0], train)
# predict = map(lambda u: u[1:], test)
# actual = map(lambda u: u[0], test)

# poly = PolynomialFeatures(degree=2)
# X_ = poly.fit_transform(X)

# clf = linear_model.LinearRegression()
# clf.fit(X_, vector)

# predict_ = poly.fit_transform(predict)
# _actual = clf.predict(predict_)

# print sum(map(lambda u: (u[0]-u[1])**2, izip(actual, _actual.tolist())))/len(actual)

# exit(0)



X = [[0.44, 0.68], [0.99, 0.23], [0.55, 0.03]]
vector = [109.85, 155.72, 99]
predict= [0.49, 0.18]
predict= [[0.44, 0.68], [0.99, 0.23], [0.55, 0.03]]

poly = PolynomialFeatures(degree=2)
X_ = poly.fit_transform(X)
predict_ = poly.fit_transform(predict)

clf = linear_model.LinearRegression()
clf.fit(X_, vector)
print clf.predict(predict_)

exit(0)

import numpy as np
x = np.array([0.0, 1.0, 2.0, 3.0,  4.0,  5.0])
y = np.array([0.0, 1.0, 0.0, -1, -2, -3])
# y = np.indices((6, 2))
print y, type(y)
z = np.polyfit(x, y, 2)

p = np.poly1d(z)
print p(6)

exit(0)


s = []
d1, d2 = 0, 0
for line in open("times.txt"):
    s.append(map(int, line.split()))
for t in s:
    d1 += abs(t[1]-t[0])
    d2 += abs(t[2]-t[0])
print d1/1000000.0, d2/1000000.0
exit(0)

# bar
def bar():
    for i in range(100):
        print "Tick"
        #time.sleep(1)

if __name__ == '__main__':
    # Start bar as a process
    p = multiprocessing.Process(target=bar)
    p.start()

    # Wait for 10 seconds or until process finishes
    p.join(10)

    # If thread is still active
    if p.is_alive():
        print "running... let's kill it..."

        # Terminate
        p.terminate()
        p.join()


# open('ss.txt', 'w').writelines(str(i)+'-' for i in range(1000000))
# print open('ss.txt').read()

exit(0)
#  like ctypes a lot, swig always tended to give me problems. Also ctypes has the advantage that you don't need to satisfy any compile time dependency on python, and your binding will work on any python that has ctypes, not just the one it was compiled against.

# Suppose you have a simple C++ example class you want to talk to in a file called foo.cpp:

# #include <iostream>

# class Foo{
#     public:
#         void bar(){
#             std::cout << "Hello" << std::endl;
#         }
# };
# Since ctypes can only talk to C functions, you need to provide those declaring them as extern "C"

# extern "C" {
#     Foo* Foo_new(){ return new Foo(); }
#     void Foo_bar(Foo* foo){ foo->bar(); }
# }
# Next you have to compile this to a shared library

# g++ -c -fPIC foo.cpp -o foo.o
# g++ -shared -Wl,-soname,libfoo.so -o libfoo.so  foo.o
# And finally you have to write your python wrapper (e.g. in fooWrapper.py)

# from ctypes import cdll
# lib = cdll.LoadLibrary('./libfoo.so')

# class Foo(object):
#     def __init__(self):
#         self.obj = lib.Foo_new()

#     def bar(self):
#         lib.Foo_bar(self.obj)
# # Once you have that you can call it like

# f = Foo()
# f.bar() #and you will see "Hello" on the screen



from ctypes import cdll
lib = cdll.LoadLibrary('./libfoo.so')
#lib.pp()
lib.print_help()
exit(0)


with open('ss.txt', 'w') as f:
  f.writelines(["asd", "zxcf", "vvv"])


lst = extract_columns('my_log.swf', (1,8,9))
print len(lst), len(lst[0])
lst = normalize_mat(lst)
print len(lst), len(lst[0])
print conv_features_list(lst, 7)
exit(0)


print str(sys.argv), sys.argv[1]
compute_utilisation(sys.argv[1])
exit(0)


from scheduling_performance_measurement import *
from abc import ABCMeta, abstractmethod

PerfMeasure = BoundedSlowdown

bsld = PerfMeasure('my_log.swf')
print bsld.average()
sld = Slowdown('my_log.swf')
print sld.all()

print bsld

# import progressbar
# widgets = ['# Jobs Terminated: ', progressbar.Counter(),' ',progressbar.Timer()]
# pbar = progressbar.ProgressBar(widgets=widgets,maxval=10000000, poll=0.1).start()
# for i in range(1000000):
# 	pbar.update(i)
# exit(0)


fn = time.strftime("%Y-%m-%d#%s") + '.tar'
files = ['log.swf', 'mini.swf', 'output/new_l2r_sim_l2r.swf']
#os.system("tar -cf {0} {1}".format(fn, ' '.join(files)))
#os.system("mv {0} {1}/{0}".format(fn, 'results'))

#globals(), locals(), vars(), and dir() may all help you in what you want.


import sys
sys.path.append("..")

from base.docopt import docopt

from run_simulator import parse_and_run_simulator
from swf_splitter import split_swf
from swf_converter import conv_features

from datetime import timedelta
import os
import gc

