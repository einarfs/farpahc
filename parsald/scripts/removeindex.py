#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, sys

inputfile = sys.argv[1]
intext = open(inputfile,'r').read()
intext = intext.replace('.-.','.')
intext = intext.replace(',-,',',')
intext = intext.replace(';-;',';')
intext = intext.replace(':-:',':')
intext = intext.replace('!-!','!')
intext = intext.replace('?-?','?')

intext = re.sub('([A-Z])([-=][0-9])+ ','\\1 ',intext)

intext = re.sub('([A-Z12])-([A-Z])','\\1*\\2',intext)

intext = intext.replace('<dash/>','-') 

print(intext)



