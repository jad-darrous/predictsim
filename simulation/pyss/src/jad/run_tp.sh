#!/bin/bash

# for file in logs/*; do
#   echo ${file##*/}
# done

echo "Sarte time:" $(date)

rm -f results/results.txt
touch results/results.txt

fname=$1
for i in `seq 32 32 192`;
#for i in `seq 16 32 64 96 128 160 192`;
do
	echo "::::::::::::: " $i " :::::::::::::"
	pypy -OO run.py $fname $i >> results/results.txt
done

echo "Finish time:" $(date)