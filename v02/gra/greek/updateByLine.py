"""updateByLine.py  Begun Apr 10, 2014
 This program is intended to be rather general.
 The 'changein' file consists of a sequence of line pairs:
 nn old old-text
 nn new new-text
 nn is the line number (starting at 1) in the input vcp file.
 'old' and 'new' are fixed.
 old-text should be identical to the text of line nn in input vcp file.
 new-text is the replacement for line nn, written to the output vcp file.
 'changein' file should be utf-8 encoded.
 Nov 16, 2014 comment line
 May 30, 2017.  Allow for 'ins' (insert) and 'del' (delete) in addition to 'new'
   1234 old xyz
   1234 ins uvw
   1234 old xyz
   1234 del 
 NOTE: This introduces complications regarding line numbers.
  The interpretation is that 
  (a) the line number (1234) represents the line number in the INPUT file
  (b) For 'ins', the inserted line ('uvw') is inserted AFTER this line
  (c) For 'del', the text part is ignored (should typically be blank,
      and there should be a space character after 'del': '1234 del '
 Nov 27, 2018. Changed print X to print(X), for python3 compatibility.
"""
#
from __future__ import print_function
import re,sys
import codecs
class Change(object):
 def __init__(self,n,oldline,newline):
  self.n = n
  m = re.search(r'^([0-9]+) old (.*)$',oldline)
  m1 = re.search(r'^([0-9]+) (new|ins|del) (.*)$',newline)
  if (not m) or (not m1):
   print('Change error(1) @ line %s:' % n)
   out= 'oldline=%s' % oldline
   print(out.encode('utf-8'))
   out= 'newline=%s' % newline
   print(out.encode('utf-8'))
   exit(1)
  self.chgcode = m1.group(2)
  nold = m.group(1)
  m = re.search(r'^([0-9]+) old (.*)$',oldline)
  oldtext = m.group(2)
  nnew = m1.group(1)
  newtext = m1.group(3)
  if nold != nnew:
   print('Change error(2) @ line %s:' % n)
   print('nold(%s) != nnew(%s)' % (nold,nnew))
   out= 'oldline=%s' % oldline
   print(out.encode('utf-8'))
   out= 'newline=%s' % newline
   print(out.encode('utf-8'))
   exit(1)   
  if (not m) or (not m1):
   print('Change error(2) @ line %s:' % n)
   out= 'oldline=%s' % oldline
   print(out.encode('utf-8'))
   out= 'newline=%s' % newline
   print(out.encode('utf-8'))
   exit(1)
  self.lnumstr = nold # same as nnew
  self.oldtext = oldtext
  self.newtext = newtext

def init_changein(changein ):
 changes = [] # ret
 f = codecs.open(changein,encoding='utf-8',mode='r')
 n = 0
 sep='XXXX'
 for line in f:
  line = line.rstrip('\r\n')
  if line.startswith(';'):  # skip comment line
   continue
  n = n + 1
  if (n % 2) == 1:
   oldline = line
  else:
   newline = line
   chgrec = Change(n-1,oldline,newline)
   changes.append(chgrec)
 f.close()
 if (n % 2) != 0:
  print("ERROR init_changein: Expected EVEN number of lines in",changein)
  exit(1)
 return changes
def update(filein,changein,fileout):
 # determine change structure from changein file
 changes = init_changein(changein)
 # initialize input records
 with codecs.open(filein,encoding='utf-8',mode='r') as f:
  # recs is a list of lines, to accomodate 'ins' and 'del'
  recs = [[line.rstrip('\n\r')] for line in f]
  print(len(recs),"lines read from",filein)
 # process change records
 # counter for each type ('new','ins','del') of change record
 counter = {}
 for change in changes:
  lnum = int(change.lnumstr)
  irec = lnum - 1 # since lnum assumed to start at 1
  try:
   oldrec = recs[irec]
  except:
   print("lnum error: ",change.lnumstr)
   exit(1)
  # oldrec is a list of lines, typically with just 1 line.
  # We assume there is always at least 1 element in this tuple, and
  # that it's text matches the 'oldtext' of the change
  if len(oldrec)==0:
   print("update ERROR #1. record has been deleted for linenum=",lnum)
   exit(1)
  oldtext = oldrec[0]
  if oldtext != change.oldtext:
   print("CHANGE ERROR #2: Old mismatch line %s of %s" %(change.n,changein))
   print("Change record lnum =",lnum)
   out = "Change old text:\n%s" % change.oldtext
   print(out.encode('utf-8'))
   out = "Change old input:\n%s" % oldtext
   print(out.encode('utf-8'))
   out = "line from %s:" % filein
   print(out.encode('utf-8'))
   exit(1)
  code = change.chgcode
  # update counter
  if code not in counter:
   counter[code] = 0
  counter[code] = counter[code] + 1
  if code == 'new':  
   # a simple change. Make this to the last in list of oldrecs
   oldrec.pop()  # remove last record
   oldrec.append(change.newtext)  # insert new text at end
   recs[irec] = oldrec
  elif code == 'ins':
   # insert new text onto end of oldrec
   oldrec.append(change.newtext)
   recs[irec] = oldrec
  elif code == 'del':
   # remove text from end
   oldrec.pop()  # remove last record
   recs[irec] = oldrec
 # write all records to fileout
 fout = codecs.open(fileout,'w','utf-8')
 nout = 0
 for rec in recs:
  # rec is a list of strings, possibly empty
  for text in rec:
   fout.write("%s\n" % text)
   nout = nout + 1
 fout.close()
 # write summary of changes performed
 print(nout,"records written to",fileout)
 print("%s change transactions from %s" % (len(changes),changein))
 # summary of types of changes transacted
 codes = counter.keys()
 outarr = ["%s of type %s"%(counter[key],key) for key in codes]
 out = ', '.join(outarr)
 print(out)
if __name__=="__main__":
 filein = sys.argv[1]
 changein = sys.argv[2]
 fileout = sys.argv[3]
 update(filein,changein,fileout)

