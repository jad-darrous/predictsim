
import os
import sys
import datetime
import time
from swf_utils import *

import multiprocessing
import time

import sys
sys.path.append("..")
import jad

assert True
assert False, "-"*8
print "asdfd"
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

