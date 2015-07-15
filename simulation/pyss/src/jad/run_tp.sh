#!/bin/bash

# for file in logs/*; do
#   echo ${file##*/}
# done

echo "Sarte time:" $(date)

rm -f results/results.txt
touch results/results.txt

fname=$1
# for i in 1024;
for i in `seq 512 256 1024`;
# for i in `seq 32 32 256`;
do
	echo ":::::::::::::"  $i  ":::::::::::::"
	pypy -OO run.py $fname $i
done

echo "Finish time:" $(date)