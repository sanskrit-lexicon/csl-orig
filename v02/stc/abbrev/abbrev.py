# coding=utf-8
""" greek.py
 Reads/Writes utf-8
"""
from __future__ import print_function
import sys, re,codecs
# Make code python2, python3 compatible.
if sys.version_info[0] > 2:
    xrange = range

class Abbrev(object):
 def __init__(self,line):
  """ see readme. for format 
   
  """
  line = line.strip() # remove starting or ending whitespace
  self.line = line
  try:
   (self.abbrev,self.data) = line.split('\t')
  except:
   print('Abbrev parse error:',line)
   print(line.startswith(';'))
   print('line[0]=',line[0],line[1])
   exit(1)
  self.count = 0  # number of instances of abbreviation

def init_abbrev(filein):
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  # allow comment lines starting with semicolon.
  recs = [Abbrev(line) for line in f if not line.startswith(';')]
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

def last_minute_change(line,idx):
 """  In a few cases, an abbreviation is within {@...@} [1 case]
  or {%...%}  [86 cases]
  These are, mostly, cases where an abbreviation appears to be within an
  italic section (italic sections are iast-spelled sanskrit).
  ANd in this cases, the abbreviation is really of some Sanskrit word.
  For example: {%kiṃ n.%} pourquoi ? pourquoi faire ?
  At this stage of the computation , we have 
    {%kiṃ <ab>n.</ab>%} pourquoi ? pourquoi faire ?
  and we remove the <ab> markup. 
 """
 newlines = {
  18251:'{@arus-@}¦ <ab>nt.</ab> cicatrice. blessure.',
  68634:'{@na-cira-@}¦ {%-am -āt -eṇa%} <ab>v.</ab> {%a-cira-} ; {%-āya%} sous peu, bientôt.',
  104964:'{@masī-@}¦ ({%-ī-%}) <ab>v.</ab> {%maṣī/i-%}; {%m. -bhū-%} devenir noir, noircir.',
  110007:'{@yad-@}¦ <ab>pron.</ab> rel., <ab>nt.</ab> <ab>sg.</ab> de {%ya-%} ; <ab>conj.</ab> que (complétives) ; de sorte',
  121936:'{@vi-TṜ-@}¦ traverser, pénétrer; accorder ({%uttaraṃ  v.%} donner une',
  128059:'à la tête; {%parājñayā v.%} être aux ordres; {%priyaṃ v.%} agir avec',
  131228:"occuper <ab>qq'un</ab> de ou auprès de (<ab>loc.</ab>, rar. <ab>instr.</ab>, <ab>qqf.</ab>  {%°artham%}; {%hastaṃ v.%}",
  131229:'faire un mouvement de la main; {%vaṇīṃ v.%} élever la voix); charger',
 }
 if idx in newlines:
  newline = newlines[idx]
 else:
  newline = re.sub(r'({%[^%])*<ab>([^<]*?)</ab>([^%]*?%})',r'\1\2\3',line)
  newline = re.sub(r'({@[^@])*<ab>([^<]*?)</ab>([^@]*?@})',r'\1\2\3',newline)
 return newline
def write_changes(fileout,inlines,outlines,manuald):
 outarr = []
 for idx,oldline in enumerate(inlines):
  newline = outlines[idx]
  linenum = idx + 1
  if newline == oldline:
   continue # no change
  changearr=[]
  changearr.append('%s old %s'%(linenum,oldline))
  #newline1=last_minute_change(newline,idx)
  if linenum in manuald:
   newline1 = manuald[linenum]
  else:
   newline1 = newline
  if newline1 == newline:
   changearr.append('%s new %s'%(linenum,newline))
  else:
   changearr.append('; Please check')
   changearr.append('%s new %s'%(linenum,newline1))
   #print('%s old %s'%(linenum,oldline))
   #print('%s new %s'%(linenum,newline1))
  outarr = outarr + changearr
 # now write the changes
 with codecs.open(fileout,"w","utf-8") as f:
  for out in outarr:
   f.write(out + '\n')
 print(len(outarr)/2,"change transactions written to",fileout)

def process_abbrev_for_line(abbrev,line,idx):
 """ abbrev may occur:
    - at beginning of line
    - when preceding character is a space or left paren
 """
 if line.count(abbrev) == 0:
  return line
 new = '<ab>%s</ab>' % abbrev
 changes = [
  #(abbrev,new),  # handled at start of line
  (' '+abbrev,' '+new),
  ('('+abbrev,'('+new)
 ]
 if (abbrev[0] in ['a','e','i','o','u']) and (' ' not in abbrev):
  """ l'instr., l'abs.' etc.
  """
  changes.append(("l'" + abbrev,"l'"+new))
 if line.startswith(abbrev):
  line = line.replace(abbrev,new,1)
 parts = re.split('(<ab>.*?</ab>)',line)
 #if (idx == 115765) and (abbrev == 'a.'):print('parts=',parts)
 newparts = []
 for part in parts:
  if part.startswith('<ab>'):
   newparts.append(part)
  else:
   newpart = part
   for old,new in changes:
    newpart = newpart.replace(old,new)  # ? or (old,new,1) ?
   newparts.append(newpart)
 # reform the line
 newline = ''.join(newparts)
 return newline

def init_manual(filein):
 def parse(line):
  m = re.search(r'^([^ ]*) (old|new) (.*)$',line)
  return(m.group(1),m.group(2),m.group(3))
 d = {}
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  # allow comment lines starting with semicolon.
  lines = [line.rstrip('\r\n') for line in f if not line.startswith(';')]
 for i,line in enumerate(lines):
  if (i % 2) == 0:
   lnum1,code1,old = parse(lines[i])
   lnum2,code2,new = parse(lines[i+1])
   if (lnum1 != lnum2) or (code1 != 'old') or (code2 != 'new'):
    print('init_manual error',i,line)
    exit(1)
  lnum = int(lnum1)
  d[lnum] = new
 return d

if __name__=="__main__":
 filein = sys.argv[1] # old.txt
 filein1 = sys.argv[2] # abbreviation file. 
 filein2 = sys.argv[3] # manual change lines
 fileout = sys.argv[4] # new.txt
 # lines of old.txt
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
    inlines = [line.rstrip('\r\n') for line in f]
 entries = init_entries(inlines)
 recs = init_abbrev(filein1)
 manuald = init_manual(filein2)
 # sort in descending order of length, since some abbreviations
 # 'overlap'. Eg. v. s. and v. s. v.  We want to markup the longer
 # ones first.
 recs_sort = sorted(recs,key = lambda rec: len(rec.abbrev),reverse=True)
 print(len(recs),"from",filein1)
 #outlines = [x for x in inlines]
 #for rec in recs_sort:
 # print(rec.abbrev)
 outlines = []
 for idx,line in enumerate(inlines):
  skip = False
  if (idx < 328) or (idx>164314):  # skip preface and appendix
   skip = True
  elif line.startswith(('<L>','<LEND>')):
   skip = True
  elif re.search(r'^ *$',line):
   skip = True
  if skip:
   outlines.append(line)
   continue
  # mark abbreviations for this line
  #if idx == 115765:print('check',idx+1,line)
  for rec in recs_sort:
   line = process_abbrev_for_line(rec.abbrev,line,idx)
   #if idx == 115765:print('check',idx+1,line,'  [%s]'%rec.abbrev)
    
  outlines.append(line)
  # check for anomalies
  parts = re.split(r'(<ab>.*?</ab>)',line)
  found = False
  for part in parts:
   if not part.startswith('<ab>'):
    for rec in recs_sort:
     abbrev = rec.abbrev.replace('.','[.]')
     if re.search(r'[ (]' +abbrev,part):
      print('part=',part,'abbrev=',abbrev)
      found = True
      exit(1)
      break
   if found:
    break
  if found:
   print('anomaly line',idx+1,inlines[idx],'\n',line)
 #print_stats(recs)  # counts
 write_changes(fileout,inlines,outlines,manuald)

