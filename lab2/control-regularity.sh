#!/bin/sh
# usage: ./memory-regularity.sh /path/to/stats.txt
file="$1"/stats.txt
val1=$(grep branchPred.condIncorrect $file | awk '{print $2}')
val2=$(grep branchPred.condPredicted $file | awk '{print $2}')

result=$(echo "scale=3; 1- ($val1 / $val2)" | bc)
echo $result
