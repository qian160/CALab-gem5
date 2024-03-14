#!/bin/sh
# usage: ./simSeconds.sh /path/to/stats.txt
file="$1"/stats.txt
val1=$(grep simSeconds $file | awk '{print $2}')

echo $val1
