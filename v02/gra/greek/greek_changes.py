# coding=utf-8
""" greek.py
 Reads/Writes utf-8
"""
from __future__ import print_function
#import xml.etree.ElementTree as ET
import sys, re,codecs
# Make code python2, python3 compatible.
if sys.version_info[0] > 2:
    xrange = range

class Greek(object):
 def __init__(self,line):
  """ see readme.org for format 
   example: lemma_sU_10078	σεύω (ἐσσύμενος); υἱός
  """
  line = line.strip() # remove starting or ending whitespace
  self.line = line
  (self.head,self.data) = line.split('\t')
  (_,self.hw,self.L_vedaweb) = self.head.split('_')
  self.greekarr = self.data.split(';')
  # there are no decimal-points in entries... file; so 'int' works.
  self.Lnum = int(self.L_vedaweb) + 1 # see comment in readme for +1
  self.Lid = str(self.Lnum)

def init_greek(filein):
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  # allow comment lines starting with semicolon.
  recs = [Greek(line) for line in f if not line.startswith(';')]
 return recs

# Entry and init_entries modified from
# csl-pywork/v02/makotemplates/hw.py and parseheadline.py
def parseheadline(headline):
 """<L>16850<pc>292-3<k1>visarga<k2>visarga<h>1<e>2"""
 headline = headline.strip()
 splits = re.split('[<]([^>]*)[>]([^<]*)',headline)
 #print(splits)
 result = {}
 for i in xrange(len(splits)):
  if i % 3 == 1:
   result[splits[i]] = splits[i+1]
 return result

class Hwmeta(object):
 # class variables for efficiency
 # The structure of the 'meta' line
 # Assume meta line within xxx.txt is a sequence of key-value pairs
 # coded as
 # <key>val
 """
#%if dictlo == 'mw':
 keysall_list = ['L','pc','k1','k2','h','e']  # standard order
#%else:
# keysall_list = ['L','pc','k1','k2','h']  # standard order
#%endif
# keysall_list = ['L','pc','k1','k2','h']  # standard order
 """
 keysall_list = ['L','pc','k1','k2','h']  # standard order
 # hom is optional
 keysneeded = set(keysall_list).difference(set(['h']))
 # significance of 'e' unclear. Ignore
 keysall = set(keysall_list)
 def __init__(self,line):
  line = line.rstrip('\r\n')
  d = parseheadline(line)
  # check for validity of keys
  keys = set(d.keys())
  if not(self.keysneeded.issubset(keys)):
   # error
   print("Hwmeta init error",line.encode('utf-8'))
   print("keysneeded=",self.keysneeded)
   print("keys=",keys)
   exit(1)
  self.d = d  
  # convert dictionary to object attributes (except for 'e' = extra)
  self.pc = d['pc']
  self.L = d['L']
  self.key1 = d['k1']
  self.key2 = d['k2']
  self.h = None
  if 'h' in d:
   self.h = d['h']
#%if dictlo == 'mw':
#  self.e = d['e']
#%endif

class Entry(object):
 Ldict = {}
 def __init__(self,lines,linenum1,linenum2):
  self.metaline = lines[0]
  self.lend = lines[-1]  # the <LEND> line
  self.datalines = lines[1:-1]  # the non-meta lines
  # parse the meta line into an Hwmeta object
  self.meta = Hwmeta(self.metaline)
  self.linenum1 = linenum1
  self.linenum2 = linenum2
  L = self.meta.L
  if L in self.Ldict:
   print("Entry init error: duplicate L",L,linenum1)
   exit(1)
  self.Ldict[L] = self

def init_entries(lines):
 # slurp lines
 #with codecs.open(filein,encoding='utf-8',mode='r') as f:
 # lines = [line.rstrip('\r\n') for line in f]
 recs=[]  # list of Entry objects
 inentry = False  
 idx1 = None
 idx2 = None
 for idx,line in enumerate(lines):
  if inentry:
   if line.startswith('<LEND>'):
    idx2 = idx
    entrylines = lines[idx1:idx2+1]
    linenum1 = idx1 + 1
    linenum2 = idx2 + 1
    entry = Entry(entrylines,linenum1,linenum2)
    recs.append(entry)
    # prepare for next entry
    idx1 = None
    idx2 = None
    inentry = False
   elif line.startswith('<L>'):  # error
    print('init_entries Error 1. Not expecting <L>')
    print("line # ",idx+1)
    print(line.encode('utf-8'))
    exit(1)
   else: 
    # keep looking for <LEND>
    continue
  else:
   # inentry = False. Looking for '<L>'
   if line.startswith('<L>'):
    idx1 = idx
    inentry = True
   elif line.startswith('<LEND>'): # error
    print('init_entries Error 2. Not expecting <LEND>')
    print("line # ",idx+1)
    print(line.encode('utf-8'))
    exit(1)
   else: 
    # keep looking for <L>
    continue
 # when all lines are read, we should have inentry = False
 if inentry:
  print('init_entries Error 3. Last entry not closed')
  print('Open entry starts at line',idx1+1)
  exit(1)

 print(len(lines),"lines read from",filein)
 print(len(recs),"entries found")
 return recs

def write_changes(fileout,recs,inlines):
 outarr = []
 for rec in recs:
  Lid,entry_hw,greeklines = rec.greekrecs
  changearr=[]
  for idx,newline in greeklines:
   changearr.append('; L=%s, hw=%s' %(Lid,entry_hw))
   linenum = idx + 1
   oldline = inlines[idx]
   changearr.append('%s old %s'%(linenum,oldline))
   changearr.append('%s new %s'%(linenum,newline))
  outarr = outarr + changearr
 # now write the changes
 with codecs.open(fileout,"w","utf-8") as f:
  for out in outarr:
   f.write(out + '\n')
 print(len(outarr)/3,"change transactions written to",fileout)

def process_greek(rec,inlines):
 # set value of rec.greekrecs,
 # a triple: L,hw,greeklines
 # where greeklines is an array of 2-tuples:
 #   (idx,newline)  where idx is an index into inlines
 Lid = rec.Lid
 if Lid == '6675':
  # example lemma_mar_6674	μαρμαίρω
  Lid = '6675.1'
 if Lid not in Entry.Ldict:
  print('process_greek ERROR 1:',rec.line)
  exit(1)
 entry = Entry.Ldict[Lid]
 entry_hw = entry.meta.key1
 if entry_hw != rec.hw:
  print('process_greek ERROR 2:',rec.line)
  print(entry_hw,' != ',rec.hw)
  exit(1)
 greekarr = rec.greekarr
 ngreekarr = len(greekarr)
 greeklines = []  # 
 idx1 = entry.linenum1 - 1
 idx2 = entry.linenum2 - 1
 igreekarr = 0
 ngreekpatterns_tot = 0
 for idx in range(idx1,idx2+1):
  line = inlines[idx]
  #print('* ',idx,line)
  old = '<lang n="greek"></lang>'
  greekpatterns = re.findall(old,line)
  ngreekpatterns = len(greekpatterns)
  ngreekpatterns_tot = ngreekpatterns_tot + ngreekpatterns
  if ngreekpatterns == 0:
   continue
  for i in range(0,ngreekpatterns):
   greek = greekarr[igreekarr]
   greek = greek.strip() # remove leading, trailing spaces
   # In one case, the change is to hebrew language, not greek
   # Namely, the 2nd change (igreekarr=1) with Lid = 4812
   if (Lid == '4812') and (igreekarr == 1):
    new = '<lang n="hebrew">%s</lang>'%greek
   else:
    new = '<lang n="greek">%s</lang>'%greek
   # the '1' means just change 1 instance in line.
   # needed as there are a few cases where two old patterns are found,
   # thus consuming 2 elements of greekarr
   line = re.sub(old,new,line,1)
   igreekarr = igreekarr + 1 # prepare for next greek 
  greeklines.append((idx,line))
 if ngreekpatterns_tot != ngreekarr:
  print('process_greek. Error 3:',ngreekpatterns_tot,ngreekarr)
  print(rec.line)
 rec.greekrecs = (Lid,entry_hw,greeklines)

if __name__=="__main__":
 filein = sys.argv[1] # old.txt
 filein1 = sys.argv[2] # vedaweb input. 
 fileout = sys.argv[3] # new.txt
 # lines of old gra.txt
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
    inlines = [line.rstrip('\r\n') for line in f]
 entries = init_entries(inlines)
 recs = init_greek(filein1)
 print(len(recs),"from",filein1)
 for irec,rec in enumerate(recs):
  process_greek(rec,inlines)
 write_changes(fileout,recs,inlines)

