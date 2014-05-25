#!/bin/bash
NR=$1
java -Dfile.encoding=UTF-8 -cp ../stanford-parser-full-2014-01-04/stanford-parser.jar -mx1g edu.stanford.nlp.parser.lexparser.LexicalizedParser -PCFG -saveToSerializedFile grammar_f_${NR}.ser.gz -vMarkov 1 -uwm 0 -headFinder edu.stanford.nlp.trees.LeftHeadFinder -train far_split${NR}training.psd -test ../farchunks/far_split${NR}testing.psd > parseroutput${NR}.txt
