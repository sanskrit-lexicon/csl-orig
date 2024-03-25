#-*- coding:utf-8 -*-
""" make_hwextra.py
 
"""
from __future__ import print_function
import sys,re,codecs

def read_lines(filein):
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  lines = [x.rstrip('\r\n') for x in f]
 return lines

def extract(lines):
 # non-comment
 ans = [line for line in lines if not line.startswith(';')]
 return ans

def write(fileout,lines):
 with codecs.open(fileout,"w","utf-8") as f:
  for out in lines:
   f.write(out+'\n')
 print(len(lines),"records written to",fileout)

if __name__=="__main__":
 filein = sys.argv[1] # multik2
 fileout = sys.argv[2] # multik2a
 lines = read_lines(filein)
 hwextras = extract(lines)
 write(fileout,hwextras)


 
