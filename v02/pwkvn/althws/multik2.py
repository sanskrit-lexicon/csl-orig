#-*- coding:utf-8 -*-
"""multik2.py
 
"""
from __future__ import print_function
import sys,re,codecs
import digentry  

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

def write(fileout,lines):
 with codecs.open(fileout,"w","utf-8") as f:
  for iline,line in enumerate(lines):
   f.write(line+'\n')
 print(len(lines),"records written to",fileout)

if __name__=="__main__":
 filein = sys.argv[1] # pwkvn.txt
 fileout = sys.argv[2] # pwhvn_hwextra.txt

 entries = digentry.init(filein)
 althws = multik2s(entries)
 
 write(fileout,althws)
 

 
