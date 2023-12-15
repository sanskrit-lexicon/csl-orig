#-*- coding:utf-8 -*-
"""multik2a.py
 
"""
from __future__ import print_function
import sys,re,codecs

def read_lines(filein):
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  lines = [x.rstrip('\r\n') for x in f]
 return lines

class Rec(object):
 def __init__(self,line):
  self.line = line
  (self.L,self.L1,self.pc,self.k1,self.k2) = line.split('\t')
  self.k2s = self.k2.split(', ')
  assert len(self.k2s) > 1
  self.k1s = []
  self.Ls = []
  self.hwextras = []

def generate_Ls(L0,L1,n):
 """
  A difficult problem in general.
  Assume L0 and L1 are digit sequences. 
   (or, L1 may be None)
 """
 n0 = int(L0)
 if L1 == None:
  n1 = n0 + 1
 else:
  n1 = int(L1)
 assert (n0 < n1),"generate_Ls ERROR 1: L0=%s, L1=%s" % (L0,L1)
 # construct intermediate values
 assert (1<=n) and (n<100),"generate_Ls ERROR 1: L0=%s, L1=%s" % (L0,L1)
 xn0 = float(n0)
 xn1 = float(n1)
 ans = []
 if (n<10):
  x = xn0
  for k in range(n):
   x = x + 0.1
   L = '%0.1f' % x
   ans.append(L)
 else: # 10<=n<=99
  x = xn0
  for k in range(n):
   x = x + 0.01
   L = '%0.2f' % x
   ans.append(L)
 return ans

def multik2s(entries):
 """ construct tab-delimited records needed for construction of hwextra
 """
 althws = []
 nentries = len(entries)
 for ientry,entry in enumerate(entries):
  metaline = entry.metaline
  L0 = entry.metad['L']
  pc0 = entry.metad['pc']
  k10 = entry.metad['k1']
  k20 = entry.metad['k2']
  if not (',' in k20):
   # no alternates for this entry
   continue
  # Get L for next entry, or None if this is last entry
  metacalc = '<L>%s<pc>%s<k1>%s<k2>%s' %(L0,pc0,k10,k20)
  # only L0,pc0,k10,k20 should be in metaline
  if metaline != metacalc:
   print('WARNING: metaline=%s' % metaline)
   print('         metacalc=%s' % metacalc)
         
  
  ientry1 = ientry+1
  if ientry1 < nentries:
   entry1 = entries[ientry1]
   L1 = entry1.metad['L']
  else:
   L1 = None
  vals = (L0,L1,pc0,k10,k20)
  out = '\t'.join(vals)
  althws.append(out)
 print(len(althws),"metalines with comma")
 return althws

def parse_k2(x):
 """ x = h k2  OR x = k2
 """
 parts = x.split(' ')
 if len(parts) == 2:
  k2 = parts[1]
  m = re.search(r'^([0-9])\.$',parts[0])
  if m == None:
   print('parse_k2 ERROR 1:',x)
   h = None
  else:
   h = m.group(1)
 else:
  h = None
  k2 = parts[0]
 # k1 strips away accents,-,*
 k1 = re.sub(r'[/\^*-]','',k2)
 return h,k1

def parse_k2s(rec):
 for k2 in rec.k2s:
  hom,k1 = parse_k2(k2)
  rec.k1s.append(k1)
 # check that rec.k1 = rec.k1s[0]
 if rec.k1 != rec.k1s[0]:
  print('parse_k2s error:',rec.line)

def generate_Ls_manual(L0,L1,n):
 # special cases for Grassman
 if (L0,L1,n) == ('6754.1','6755',1):
  ans = ['6754.2']
 elif (L0,L1,n) == ('6881','6881.5',1):
  ans = ['6881.1']
 else:
  ans = []
 if ans != []:
  print('generate_Ls_manual: %s,%s,%s -> %s' % (L0,L1,n,ans))
 return ans

def generate_Ls(L0,L1,n):
 """
  A difficult problem in general.
  Assume L0 and L1 are digit sequences. 
   (or, L1 may be None)
 """
 ans = generate_Ls_manual(L0,L1,n)
 if ans != []:
  return ans
 # use a computation
 n0 = int(L0)
 if L1 == None:
  n1 = n0 + 1
 else:
  n1 = int(L1)
 assert (n0 < n1),"generate_Ls ERROR 1: L0=%s, L1=%s" % (L0,L1)
 # construct intermediate values
 assert (1<=n) and (n<100),"generate_Ls ERROR 1: L0=%s, L1=%s" % (L0,L1)
 xn0 = float(n0)
 xn1 = float(n1)
 ans = []
 if (n<10):
  x = xn0
  for k in range(n):
   x = x + 0.1
   L = '%0.1f' % x
   ans.append(L)
 else: # 10<=n<=99
  x = xn0
  for k in range(n):
   x = x + 0.01
   L = '%0.2f' % x
   ans.append(L)
 return ans

def compute_Ls(rec):
 L = rec.L
 L1 = rec.L1
 n = len(rec.k2s) - 1 # number of extra Ls
 extra_Ls = generate_Ls(L,L1,n)
 for i,k1 in enumerate(rec.k1s):
  if i == 0:
   rec.Ls.append(rec.L)
  else:
   Lnext = extra_Ls[i-1]
   rec.Ls.append(Lnext)

def hwextras(rec):
 ans = []
 # the parents
 lp = rec.L
 k1p = rec.k1
 k2 = rec.k2
 pc = rec.pc
 t = 'alt' # type
 for i,k1 in enumerate(rec.k1s):
  if i == 0:  # the original metaline
   continue
  L = rec.Ls[i]
  out = '<L>%s<pc>%s<k1>%s<k2>%s<type>%s<LP>%s<k1P>%s' %(
       L,pc,k1,k2,t,lp,k1p)
  ans.append(out)
 rec.hwextras = ans

def write(fileout,recs):
 n = 0
 outarr = []
 for rec in recs:
  outarr.append('; %s' % rec.line)
  for hwextra in rec.hwextras:
   outarr.append(hwextra)
   n = n + 1
   
 with codecs.open(fileout,"w","utf-8") as f:
  for out in outarr:
   f.write(out+'\n')
 print(len(recs),"records written to",fileout)
 print(n,'extra headwords')

if __name__=="__main__":
 filein = sys.argv[1] # multik2
 fileout = sys.argv[2] # multik2a
 lines = read_lines(filein)
 recs = [Rec(line) for line in lines]
 
 for rec in recs:
  parse_k2s(rec)
  compute_Ls(rec)
  hwextras(rec)
 write(fileout,recs)
 

 
