#-*- coding:utf-8 -*-
"""deva.py convert pwkvn from slp1 to devanagari
 
"""
from __future__ import print_function
import sys,re,codecs
import transcoder
transcoder.transcoder_set_dir('./')

def transcode_deva_meta(line,tranin,tranout):
 """  assume <k1>X<k2>Y  and Y is end of line
 """
 def f(m):
  tag = m.group(1)
  x = m.group(2)
  rest = m.group(3)
  y = transcoder.transcoder_processString(x,tranin,tranout)
  return '%s%s%s' %(tag,y,rest)
 
 newline = re.sub(r'(<k1>)(.*?)(<)',f,line)
 newline = re.sub(r'(<k2>)(.*?)($)',f,newline)
 return newline

def transcode_deva_general(line,tranin,tranout):
 def f(m):
  x = m.group(1)
  parts = re.split(r'(\[Page.*?\])|(<.*?>)',x)
  newparts = []
  for part in parts:
   if part == None:
    continue
   elif part.startswith('[Page'):
    newpart = part
   elif part.startswith('<'):
    newpart = part
   else:
    newpart = transcoder.transcoder_processString(part,tranin,tranout)
   newparts.append(newpart)
  y = ''.join(newparts)
  return '{#%s#}' % y
 newline = re.sub(r'{#(.*?)#}',f,line)
 return newline

def transcode_deva(line,opt1,opt2):
 if line.startswith('<L>'):
  return transcode_deva_meta(line,opt1,opt2)
 else:
  return transcode_deva_general(line,opt1,opt2)


def convert1(line,opt1,opt2,iline):
 newline = transcode_deva(line,opt1,opt2)
 return newline

def convert(lines,opt1,opt2):
 newlines = []
 for iline,line in enumerate(lines):
  newline = convert1(line,opt1,opt2,iline)
  newlines.append(newline)
 return newlines

def write(fileout,lines):
 with codecs.open(fileout,"w","utf-8") as f:
  for iline,line in enumerate(lines):
   f.write(line+'\n')
 print(len(lines),"records written to",fileout)

if __name__=="__main__":
 opt1,opt2 = sys.argv[1].split(',')  # deva,slp1 or slp1,deva
 assert (opt1,opt2) in [('deva','slp1'),('slp1','deva')]

 filein = sys.argv[2] # 
 fileout = sys.argv[3] # 
 
 with codecs.open(filein,"r","utf-8") as f:
  lines = [x.rstrip('\r\n') for x in f]
  print(len(lines),"lines read from",filein)

 newlines = convert(lines,opt1,opt2)
 write(fileout,newlines)
  
 
