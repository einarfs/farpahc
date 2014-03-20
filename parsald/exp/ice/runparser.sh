#!/bin/bash
# usage: 
# runparser.sh NUMBER
# where number is the number of the split in the cross-val, 0-9
split=$1
start=$(date +%s)

grammar_file="grammars/ice300k.gr"
input_file="../ei1/corpus/far_split"${split}"testing.txt"
output_file=$"output/far_split"${split}"machineparsed.psd"

# run parser
java -jar ../../BerkeleyParser-1.7.jar -gr $grammar_file -inputFile $input_file -outputFile $output_file

end=$(date +%s)
diff=$(( $end - $start ))
echo "Machine parsing of test chunk $split in seconds: $diff"



