#!/bin/bash

# for file in logs/*; do
#   echo ${file##*/}
# done

echo "Sarte time:" $(date)

for file in `ls logs/*.swf`;
do
	echo $file # ${file##*/}
	fname=$(basename $file)
	pypy -OO run.py $file -wr
done

echo "Finish time:" $(date)