#!/bin/bash
# usage: 
# train.sh NUMBER 
# where number is the number of the split in the cross-val, 0-9
split=$1
start=$(date +%s)

training_file="corpus/icepahc300.psd"
grammar_file="grammars/icepahc300k.gr"
training_report="grammars/icepahc300report.txt"
time_report="grammars/ice300trainingtime.txt"
echo $training_file

# train parser
java -Xmx32768M -cp ../../BerkeleyParser-1.7.jar edu.berkeley.nlp.PCFGLA.GrammarTrainer -path $training_file -out $grammar_file -treebank SINGLEFILE > $training_report

end=$(date +%s)
diff=$(( $end - $start ))
echo "Training on full set in seconds: $diff" > $time_report




