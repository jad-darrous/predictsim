#!/bin/bash

# for file in logs/*; do
#   echo ${file##*/}
# done

echo "Sarte time:" $(date)

rm -f results/results.txt
touch results/results.txt

#for file in `find logs/main -type f -name "*.swf"`;
#for file in logs/*.swf;
#for file in `ls logs/*.swf`;
#for file in logs/CEA-curie_log.swf logs/SDSC-BLUE_log.swf logs/Metacentrum2013.swf;
for file in logs/KTH-SP2_log.swf logs/CTC-SP2_log.swf logs/SDSC-SP2_log.swf logs/SDSC-BLUE_log.swf;
do
	echo '+-----------------------'
	echo '|' $file # ${file##*/}
	echo '+-----------------------'
	fname=$(basename $file)
	pypy -OO run.py $file -o #> results/$fname.out
done

NOW=$(date +"%F#%H_%M")

# cp conf.py results/conf.py
# cd results
# tar -cf $NOW.tar *_log.swf.out conf.py results.txt
# cd ..

echo "Results are saved in $NOW.tar file"

echo "Finish time:" $(date)