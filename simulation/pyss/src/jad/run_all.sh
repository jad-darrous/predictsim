#!/bin/bash

# for file in logs/*; do
#   echo ${file##*/}
# done

for file in logs/*.swf; do
  	# echo ${file##*/}
	echo $(basename $file), $file
  	i=${file##*/}
  	cp logs/$i $i
  	pypy -OO run.py $i > $i.out
 	tar -cf $i.tar $i.out output2
 	rm $i.out $i
 	mv $i.tar results/$i.tar
done
