#!/bin/bash
python2.4 base/test_prototype.py $*
PYTHONPATH=.:$PYTHONPATH python2.4 schedulers/tests.py $*
