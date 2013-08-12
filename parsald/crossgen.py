#!/usr/bin/python
# -*- coding: utf-8 -*-

directory = 'trainingcorpus/'
cprefix = 'far_'

inputfile = open('testinput1.psd','r').read()
tokens = inputfile.split('\n\n')

for splitset in range(0,10):
  currenttraining = []
  currentgold = []
  for tokenid in range(0,len(tokens)):
    if tokenid % 10 == splitset:
      currentgold.append( tokens[tokenid] )
    else:
      currenttraining.append( tokens[tokenid] )
  #write split set X
  training = open(directory + cprefix+'split'+str(splitset)+'training.psd','w')
  training.write('\n\n'.join(currenttraining))

  gold = open(directory + cprefix+'split'+str(splitset)+'gold.psd','w')
  gold.write('\n\n'.join(currentgold))


