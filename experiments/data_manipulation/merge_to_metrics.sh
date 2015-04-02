#!/bin/bash
 
change=0
args=$@


for v in $args
do
	if test $change -eq 0
	then
		cat $v | sed 's/   / /g'
	else
		cat $v | sed 's/   / /g' |tail -1
	fi
	change=$(($change + 1))
done
