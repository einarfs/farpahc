#!/bin/bash
# usage: 
# train.sh NUMBER 
# where number is the number of the split in the cross-val, 0-9
split=$1
start=$(date +%s)

training_file="corpus/far_split"${split}"training.psd"
grammar_file="grammars/far"${split}".gr"
training_report="grammars/far"${split}"report.txt"
time_report="grammars/far"${split}"time.txt"
echo $training_file

# train parser
java -Xmx32768M -cp ../../BerkeleyParser-1.7.jar edu.berkeley.nlp.PCFGLA.GrammarTrainer -path $training_file -out $grammar_file -treebank SINGLEFILE > $training_report

end=$(date +%s)
diff=$(( $end - $start ))
echo "Training on split $split in seconds: $diff" > $time_report




