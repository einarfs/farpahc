#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
from nltk import Tree

directory = 'trainingcorpus/'
cprefix = 'far_'

inputfile = open('raw_corpus/farpahc01.psd','r').read()
tokens = inputfile.split('\n\n')

def parse2text(parse):
  out = ''
  matches = re.finditer(' ([^)(]+)',parse)
  for match in matches:
    out += match.group(1) + ' '
    #print( match.group(1) + ' ...')

  while '  ' in out:
    out = out.replace('  ',' ')
  return out.strip()

for splitset in range(0,10):
  currenttraining = []
  trainingtext = []
  currentgold = []
  goldtext = []
  for tokenid in range(0,len(tokens)):
    if tokenid % 10 == splitset:
      currentgold.append( tokens[tokenid] )
      goldtext.append( parse2text( tokens[tokenid] ) )
    else:
      currenttraining.append( tokens[tokenid] )
      trainingtext.append( parse2text( tokens[tokenid] ) ) 
  #write split set X
  training = open(directory + cprefix+'split'+str(splitset)+'training.psd','w')
  training.write('\n\n'.join(currenttraining))
  trainingtextfile = open(directory + cprefix+'split'+str(splitset)+'training.txt','w')
  trainingtextfile.write('\n'.join(trainingtext))

  gold = open(directory + cprefix+'split'+str(splitset)+'testing.psd','w')
  gold.write('\n\n'.join(currentgold))
  goldtextfile = open(directory + cprefix+'split'+str(splitset)+'testing.txt','w')
  goldtextfile.write('\n'.join(goldtext))


