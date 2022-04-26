#-*- coding:utf-8 -*-
"""hwextra.py
 
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

def make_althws(entries):
 """ look for <althws>{#A, B, ...#}</althws> on first line of entry.
  If present, construct sequence of meta-lines for A, B, etc. and
  append to output sequence of lines, which is returned
 """
 althws = []
 nentries = len(entries)
 for ientry,entry in enumerate(entries):
  m = re.search(r'<althws>{#(.*?)#}</althws>',entry.datalines[0])
  if m == None:
   continue
  hws = re.split(r', *',m.group(1))
  L0 = entry.metad['L']
  pc0 = entry.metad['pc']
  k10 = entry.metad['k1']
  k20 = entry.metad['k2']
  # Get L for next entry, or None if this is last entry
  ientry1 = ientry+1
  if ientry1 < nentries:
   entry1 = entries[ientry1]
   L1 = entry1.metad['L']
  else:
   L1 = None
  nhws = len(hws)
  Lhws = generate_Ls(L0,L1,nhws)  # this is the tricky part
  if 10 <= nhws:
   print('%s,%s,%s has %s alternate headwords' %(L0,pc0,k10,nhws))
  # generate a line for each hw
  for ihw,hw in enumerate(hws):
   L = Lhws[ihw]
   pc = pc0
   k1 = hw
   k2 = hw
   t = 'alt' #type
   lp = L0
   k1p = k10
   out = '<L>%s<pc>%s<k1>%s<k2>%s<type>%s<LP>%s<k1P>%s' %(
       L,pc,k1,k2,t,lp,k1p)
   althws.append(out)
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
 newlines = make_althws(entries)
 
 write(fileout,newlines)

 
