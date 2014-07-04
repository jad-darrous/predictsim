#!/bin/sh
echo "Scheduler: $1, no. lines: $2"
tail -$2 5K_sample | ./go.sh - $1
