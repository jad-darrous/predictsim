#!/bin/sh
cmd="time ./run_simulator.sh --num-processors=100 --input-file=$1 --scheduler=$2"
echo $cmd
$cmd
