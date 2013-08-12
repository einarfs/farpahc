#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, sys

inputfile = sys.argv[1]
intext = open(inputfile,'r').read()
print(re.sub('([A-Z])-[0-9] ','\\1 ',intext))
