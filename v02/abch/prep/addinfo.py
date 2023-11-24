#-*- coding:utf-8 -*-
"""additional info added to abch
"""
from __future__ import print_function
import sys, re,codecs

def info_1(lines):
 """
  Re 'entrydetails' -- 
 """
 newlines = [] # returned
 nchg = 0 # number of lines changed
 metaline = None
 prev_verse = None
 for iline,line in enumerate(lines):
  if line.startswith('<L>'):
   metaline = line
   newlines.append(line)
  elif line.startswith('<LEND>'):
   metaline = None
   newlines.append(line)
   # check that previous line ends with '.</s>'
   if not lines[iline-1].endswith('.</s>'):
    print('WARNING',lines[iline-1])
  elif metaline == None:
   # Not in an entry
   newlines.append(line)
   # We are in an entry
  elif not line.startswith('<s>'):
   newlines.append(line)
  else:
   # line starts with '<s>' - an entrydetail line
   m = re.search(r'[.][.] ([0-9]+) [.][.]</s>$',line)
   if m != None:
    prev_verse = int(m.group(1))
    newlines.append(line)
   else:
    ## partial verse
    nextline = lines[iline + 1]
    if nextline.startswith('<LEND>'):
     # the last line of entry
     next_verse = prev_verse + 1
     end = ' .</s>'
     if not line.endswith(end):
      # multi-line verse, e.g. at <L>48
      newlines.append
     else:
      newend = ' (%s) .</s>' % next_verse
      newline = line.replace(end, newend)
      newlines.append(newline)
      nchg = nchg + 1
    else:
     newlines.append(line)
 print(nchg,"changes in info_1")
 return newlines

def info_2(lines):
 """
  page break in entry.  
  This does not work properly to generate a new 'page' link.
  Must coordinate with make_xml.py.
  Currently, it just introduces a blank line
 """
 newlines = [] # returned
 nchg = 0 # number of lines changed
 metaline = None
 prev_verse = None
 for iline,line in enumerate(lines):
  if line.startswith('<L>'):
   metaline = line
   newlines.append(line)
  elif line.startswith('<LEND>'):
   metaline = None
   newlines.append(line)
  elif metaline == None:
   # Not in an entry
   newlines.append(line)
  elif line.startswith(';'):
   # in an entry
   # 15 lines in entries are of form ;p{nnnn}  (page break)
   # print('check meta',iline+1,line) 
   m = re.search(r'^;p{([0-9]+)}$',line)
   if m == None:
    print('info_2 unexpected',line)
    newlines.append(line)
   else:
    ipage = int(m.group(1))
    #newline = '' # '<pb>%s</pb>' % ipage  Blank line is incomplete solution
    newline = line # no change in this revision
    newlines.append(newline)
    nchg = nchg + 1
  else:
   # other kinds of lines
   newlines.append(line)
 print(nchg,"changes in info_2")
 return newlines

def make_kvvv_regexes():
 keys = ['k','v','vv']
 regexes = []
 for key in keys:
  regexraw = r'^;(%s){(.*?)}$' % key
  regex = re.compile(regexraw)
  regexes.append(regex)
 return regexes

kvvv_regexes = make_kvvv_regexes()

def info_3_kvvv(line,kvvv):
 # update kvvv from line
 prevkvvv = {}  # previous
 for key in kvvv.keys():
  prevkvvv[key] = kvvv[key]
 for regex in kvvv_regexes:
  m = re.search(regex,line)
  if m != None:
   key = m.group(1)
   value = m.group(2)
   kvvv[key] = value
 if kvvv['k'] != prevkvvv['k']:
  # When 'k' changes, initialize v and vv to ''
  kvvv['v'] = ''
  kvvv['vv'] = ''
 elif kvvv['v'] != prevkvvv['v']:
  # when 'v' changes, initialize vv
  kvvv['vv'] = '';
                            
def info_3_make_infoline(kvvv):
 parts = []
 for key in ['k','v','vv']:
  value = kvvv[key]
  if value != '':
   parts.append(value)
 attrib = ', '.join(parts)
 newline = '<info kvvv="%s"/>' %attrib
 return newline

def info_3(lines):
 """
  <info kvvv="k v vv"/>
  KaRqa, varga, upavarga
 """
 newlines = [] # returned
 nchg = 0 # number of lines changed
 metaline = None
 prev_verse = None
 kvvv = {'k' : '', 'v': '', 'vv': ''}
 for iline,line in enumerate(lines):
  if line.startswith('<L>'):
   metaline = line
   newlines.append(line)
   infoline = info_3_make_infoline(kvvv)
   newlines.append(infoline)
  elif line.startswith('<LEND>'):
   metaline = None
   newlines.append(line)
  elif metaline == None:
   # Not in an entry
   newlines.append(line)
   info_3_kvvv(line,kvvv)  # assume only occurs outside <L>..<LEND>
  else:
   # other kinds of lines
   newlines.append(line)
 print(nchg,"changes in info_2")
 return newlines

if __name__=="__main__": 
 filein = sys.argv[1] #  xxx.txt input file
 fileout = sys.argv[2] # result of conversion
 # slurp lines
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  lines = [line.rstrip('\r\n') for line in f]
 newlines = info_1(lines)
 # newlines = info_2(newlines) # page break - not implemented
 newlines = info_3(newlines) # k,v,vv
 with codecs.open(fileout,'w','utf-8') as f:
  for line in newlines:
   f.write(line+'\n')
