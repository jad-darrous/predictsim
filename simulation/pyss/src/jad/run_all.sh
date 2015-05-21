#!/bin/bash

# for file in logs/*; do
#   echo ${file##*/}
# done

rm -f results/results.txt
touch results/results.txt

for file in `find logs -type f -name "*.swf"`; do
#for file in logs/small/*.swf; do
  	# echo ${file##*/}
	echo $file
  	#fname=${file##*/}
  	fname=$(basename $file)
  	# cp logs/$fname $fname
  	pypy -OO run.py $file > results/$fname.out
 	# tar -cf $fname.tar $fname.out #output
 	# rm $fname.out $fname
 	# mv $fname.tar results/$fname.tar
 	# mv $fname.out results/$fname.out
done
