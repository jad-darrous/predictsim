#!/bin/bash

# for file in logs/*; do
#   echo ${file##*/}
# done

echo "Sarte time:" $(date)

rm -f results/results.txt
touch results/results.txt

for file in `find logs -type f -name "*.swf"`;
#for file in logs/small/*.swf; 
do
	echo $file # ${file##*/}
	fname=$(basename $file)
	pypy -OO run.py $file > results/$fname.out
done

NOW=$(date +"%F#%H_%M")

cp conf.py results/conf.py
cd results
tar -cf $NOW.tar *_log.swf.out conf.py results.txt
cd ..

echo "Results are saved in $NOW.tar file"

echo "Finish time:" $(date)