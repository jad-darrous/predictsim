#!/bin/bash
python2 base/test_prototype.py $*
PYTHONPATH=.:$PYTHONPATH python2 schedulers/tests.py $*
