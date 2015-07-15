#!/bin/bash

for i in `ls output/*.swf`;
do
	python swf_viewer.py $i $i.html -r
done
