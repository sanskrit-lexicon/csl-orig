#-*- coding:utf-8 -*-
"""convert.py   convert files from other transcodings to slp1
   assume format of abch1.txt (see readme)
"""
from __future__ import print_function
import sys, re,codecs
import transcoder
transcoder.transcoder_set_dir('transcoder')

def wrap_deva_tags(input_text,tag):
 # adapted from bing_wrapdeva.py
 # Regular expression to match Devanagari text
 devanagari_pattern = re.compile(r'[\u0900-\u097F]+')

 def replace_deva(match):
  return f"<{tag}>{match.group()}</{tag}>"

 # Replace Devanagari text with wrapped tags
 output_text = re.sub(devanagari_pattern, replace_deva, input_text)
 return output_text

def convert(line,tranin,tranout,iline):
 def f(m):
  x = m.group(1)
  y = transcoder.transcoder_processString(x,tranin,tranout)
  z = '<s>%s</s>' % y
  return z
 if tranin == 'deva':
  line1 = wrap_deva_tags(line,'s')  # <s>X</s>
  line2 = re.sub('<s>(.*?)</s>',f,line1)
  # join various deva-text fragments.
  # e.g. '</s> <s>' -> ' '
  line3 = re.sub(r'</s>([^<]+)<s>',r'\1',line2)
  # a few lines end in '</s>-'.  Move the '-' inside
  line4 = line3.replace('</s>-', '-</s>')
  return line4
 if tranin == 'slp1':
  line1 = re.sub('<s>(.*?)</s>',f,line)
  line2 = re.sub('</?s>','',line1)  # remove <s> markup in Devanagari
  return line2
 print('convert error: tranin not known:',tranin)
 exit(1)

def parse_option(option):
 # option = deva,slp1  or slp1,deva
 options = ['deva,slp1' , 'slp1,deva']
 if option not in options:
  print('convert option error',option)
  print('Allowed options = ',' OR ' . join(options))
  exit(1)
 tranin,tranout = option.split(',')
 return tranin,tranout
if __name__=="__main__": 
 option = sys.argv[1]
 tranin,tranout = parse_option(option)
 filein = sys.argv[2] #  xxx.txt file to be converted
 fileout = sys.argv[3] # result of conversion
 # slurp lines
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  lines = [line.rstrip('\r\n') for line in f]

 with codecs.open(fileout,'w','utf-8') as f:
  for iline,line in enumerate(lines):
   out = convert(line,tranin,tranout,iline)
   f.write(out+'\n')
