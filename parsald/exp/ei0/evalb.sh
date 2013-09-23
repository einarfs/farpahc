#!/bin/bash
# evaluate all splits
for i in `seq 0 9`;
do
  echo "Split"$i
  python ../../tscripts/formatgold.py "corpus/far_split"$i"testing.psd" > "gold/far_split"$i"gold.psd"
  ../../EVALB/evalb -p "../../EVALB/sample/sample.prm" "gold/far_split"$i"gold.psd" "output/far_split"$i"machineparsed.psd" > "eval/far"$i"eval.txt"
done    

#../../EVALB/evalb -p ../../EVALB/sample/sample.prm gold/far_split0gold.psd output/far_split0machineparsed.psd > eval/far0eval.txt

