#-*- coding:utf-8 -*-
"""gender_list.py
"""
from __future__ import print_function
import sys, re,codecs


def gender_freq(lines):
 """
  <eid>2294<syns><s>DArA-strI,praDi-puMstrI,nemi-strI</s>
 """
 d = {}  # gender:count dictionary. Returned
 regex = r'<syns><s>(.*?)</s>'
 metaline = None
 for iline,line in enumerate(lines):
  if line.startswith('<L>'):
   metaline = line
  elif line.startswith('<LEND>'):
   metaline = None
  elif metaline == None:
   pass
  else:
   # line within body of an entry
   m = re.search(regex,line)
   if m != None:
    syngens_str = m.group(1)
    syngens = re.split(r' *, *',syngens_str)
    for syngen in syngens:
     syn,gen = syngen.split('-')
     # update d
     if gen not in d:
      d[gen] = 0
     d[gen] = d[gen] + 1
 return d


def get_gender_names():
 d = {}
 d['a'] = 'avyayIBAva,indeclineable'
 d['klI'] = 'klIba,neuter'
 d['klIba'] = 'klIba bahuvacana,neuter plural'
 d['klIdvi'] = 'klIba dvivacana,neuter dual'
 d['puM'] = 'puMs,masculine'
 d['puMba'] = 'puMs bahuvacana,masculine plural'
 d['puMdvi'] = 'puMs dvivacana,masculine dual'
 d['puMklI'] = 'puMs klIba vA,masculine or neuter'
 d['puMklIba'] = 'puMs klIba vA bahuvacana,masculine or neuter plural'
 d['puMklIdvi'] = 'puMs klIba vA dvivacana,masculine or neuter dual'
 d['puMstrI'] = 'puMs strI vA,masculine or feminine'
 d['puMstrIba'] = 'puMs strI vA bahuvacana,masculine or feminine plural'
 d['sa'] = '?'
 d['strI'] = 'strI,feminine'
 d['strIba'] = 'strI bahuvacana,feminine plural'
 d['strIdvi'] = 'strI dvivacana,feminine dual'
 d['strIklI'] = 'strI klIba vA,feminine or neuter'
 d['tri'] = '?'
 d['vA'] = '?'
 d['vApuMklI'] = '?'
 return d

def make_outarr_1(dgen):
 gender_names_d = get_gender_names()
 outarr = []
 genders = dgen.keys()
 genders = sorted(genders)  # Latin alphabetical order
 for gen in genders:
  count = dgen[gen]
  tip = gender_names_d[gen]
  out = '%04d %s %s' %(count,gen.ljust(10),tip)
  # out = '%s %s' %(gen,count) 
  outarr.append(out)
 return outarr

def make_outarr_2(dgen):
 """ preliminary write a dictionary for gender-names
 """
 outarr = []
 genders = dgen.keys()
 genders = sorted(genders)  # Latin alphabetical order
 outarr.append(' d = {}')
 for gen in genders:
  out = " d['%s'] = ''" % gen
  outarr.append(out)
 return outarr

def write_gender(fileout,dgen):
 outarr = make_outarr_1(dgen)
 # outarr = make_outarr_2(dgen)  # preliminary
 with codecs.open(fileout,'w','utf-8') as f:
  for line in outarr:
   f.write(line+'\n')
 print(len(outarr),"records written to",fileout)
 
if __name__=="__main__": 
 filein = sys.argv[1] #  xxx.txt input file
 fileout = sys.argv[2] # list of genders with count
 # slurp lines
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  lines = [line.rstrip('\r\n') for line in f]
 d = gender_freq(lines)
 write_gender(fileout,d)
       
