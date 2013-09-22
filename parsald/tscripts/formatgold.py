#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from nltk import ParentedTree

inputfile = sys.argv[1]

parses = open(inputfile,'r').read().split('\n\n')

for parse in parses:
  t = ParentedTree(parse)
  print( t._pprint_flat(nodesep='', parens='()', quotes=False))