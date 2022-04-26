#-*- coding:utf-8 -*-
"""final.py
 
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

def transcode_as_ls_helper(x,tranin,tranout):
 parts = re.split(r'(\[Page.*?\])',x)
 newparts = []
 for part in parts:
  if part.startswith('[Page'):
   newpart = part
  else:
   newpart = transcoder.transcoder_processString(part,tranin,tranout)
  newparts.append(newpart)
 y = ''.join(newparts)
 return y
def transcode_as_ls(line,tranin,tranout):
 def f(m):
  x1 = m.group(1)
  x2 = m.group(2)
  #y1 = transcoder.transcoder_processString(x1,tranin,tranout)
  #y2 = transcoder.transcoder_processString(x2,tranin,tranout)
  y1 = transcode_as_ls_helper(x1,tranin,tranout)
  y2 = transcode_as_ls_helper(x2,tranin,tranout)
  return '<ls%s>%s</ls>' % (y1,y2)
 
 newline = re.sub(r'<ls(.*?)>(.*?)</ls>',f,line)
 return newline

def transcode_as_is(line,tranin,tranout):
 def f(m):
  x = m.group(1)
  y = transcoder.transcoder_processString(x,tranin,tranout)
  # also change markup.
  # When tranout is roman, use <is>y</is>
  # When tranout is as, use {|y|}
  if tranout == 'roman':
    return '<is>%s</is>' % y
  elif tranout == 'as':
    return '{|%s|}' % y
  else:
   print('ERROR: transcode_as_is. wrong tranout=',tranout)
   exit(1)
 if tranin == 'as':
  newline = re.sub(r'{\|(.*?)\|}',f,line)
 elif tranin == 'roman':
  newline = re.sub(r'<is>(.*?)</is>',f,line)
 else:
  print('ERROR: transcode_as_is. wrong tranin=',tranin)
 return newline

def transcode_as_as1(line,tranin,tranout):
 def f(m):
  x = m.group(1)
  y = transcoder.transcoder_processString(x,tranin,tranout)
  return '<as1>%s</as1>' % y
 
 newline = re.sub(r'<as1>(.*?)</as1>',f,line)
 return newline

def unused_transcode_as_shloka(line,tranin,tranout,iline):
 """ S4l. not (currently) within <ls>X<ls> or {|X|}
  Only a couple
 """
 if tranin == 'as':
  newline = line.replace('S4l.', 'Śl.')
 else: 
  newline = line.replace('Śl.', 'S4l.')
 if newline != line:
  print('transcode_as_shloka changed line',iline+1)
 return newline

dknown = {}

def unused_transcode_as_misc(line,tranin,tranout,iline):
 if line.startswith(('<L>','<H>')):
  return line
 if tranin != 'as':
  return line
 parts = re.split(r'\b',line)
 for part in parts:
  m = re.search(r'[a-zA-Z][0-9]',part)
  if m != None:
   if not part.startswith('Page'):
    if part in dknown:
     dknown[part] = dknown[part] + 1
     continue
    dknown[part] = 1
    #newpart = transcoder.transcoder_processString(part,tranin,tranout)
    print('as: %05d %s' % (iline+1,part))
 return line
 
 newline = transcoder.transcoder_processString(line,tranin,tranout)
 if newline != line:
  print('transcode_as_misc: lnum=',iline+1)
 return newline

def transcode_as(line,opt1,iline):
 assert opt1 in ('hk','slp1')
 if opt1 == 'hk':
  tranin = 'as'
  tranout = 'roman'
 else:
  tranin = 'roman'
  tranout = 'as'
 newline = transcode_as_ls(line,tranin,tranout)
 newline = transcode_as_is(newline,tranin,tranout)
 #newline = transcode_as_shloka(newline,tranin,tranout,iline)
 newline = transcode_as_as1(newline,tranin,tranout)
 return newline

def convert1_misc(line,opt1):
 if opt1 == 'hk':
  changes = [('º','°'),  # masc. ord. indicator <-> degree
              ('²','<lb/>')]
 else:
  changes = [('°','º'),('<lb/>','²')]
 newline = line
 for old,new in changes:
  newline = newline.replace(old,new)
 return newline

def convert1_lang(line,opt1,iline):
 changes1 = [('alpha','α'), ('beta','β'), ('gamma','γ'), 
            ('delta','δ'), ('epsilon','ε'), ('zeta','ζ')]
 # these have to be edited
 changes2 = [('greek1','ζυγόν'), ('greek2','παρθενος'), ('greek3','Ζακαστηνη')]
 def f1(m):
  x = m.group(1)
  #print('dbg. len changes2=',len(changes2))
  change = [c[1] for c in changes2 if c[0] == x]
  if change != []:
   gk = change[0]
   return '<lang n="greek">%s</lang>' %gk
  change = [c[1] for c in changes1 if c[0] == x]
  if change != []:
   gk = change[0]
   return gk
  if change == []:
   print('ERROR: convert1_lang. f1 problem at line',iline+1,'x=',x)
   exit(1)

 def f2a(m):
  x = m.group(1)
  change = [c[0] for c in changes2 if c[1] == x]
  if change != []:
   abc = change[0]
   return '<gr>%s</gr>' % abc
  print('ERROR. convert_lang. f2a problem at line',iline+1)
  exit(1)

 def f2b(m):
  x = m.group(1)
  change = [c[0] for c in changes1 if c[1] == x]
  if change != []:
   abc = change[0]
   return '<gr>%s</gr>' % abc
  print('ERROR. convert_lang. f2b problem at line',iline+1)
  exit(1)
  
 if opt1 == 'hk':
  newline = re.sub(r'<gr>(.*?)</gr>',f1,line)
 else:
  newline = re.sub(r'<lang n="greek">(.*?)</lang>',f2a,line)
  if newline == line:
   newline = re.sub(r'([αβγδεζ])',f2b,line)
 return newline

def convert1(line,opt1,opt2,iline):
 newline = transcode_deva(line,opt1,opt2)
 newline = transcode_as(newline,opt1,iline)
 newline = convert1_lang(newline,opt1,iline)
 newline = convert1_misc(newline,opt1)
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

def check_as(lines):
 nprob = 0
 for iline,line in enumerate(lines):
  if line.startswith(('<L>','<LEND>','<H>')):
   continue
  if line.strip() == '':
   continue
  line = line.replace('[Page','[Page ')
  parts = re.split(r'({\|.*?\|})|(<ls.*?>.*?</ls>)|(<as1>.*?</as1>)|(<gr>.*?</gr>)',line)
  for part in parts:
   if part == None:
    continue
   if part.startswith(('{|','<ls','<as1>','<gr>')):
    continue
   a = re.findall('[a-zA-Z][0-9]',part)
   if a == []:
    continue
   print('check_as line #%s: %s' %(iline+1,part))
   nprob = nprob + 1
 print('check_as found %s problems' %nprob)
 
if __name__=="__main__":
 opt1,opt2 = sys.argv[1].split(',')  # hk,slp1 or slp1,hk
 assert (opt1,opt2) in [('hk','slp1'),('slp1','hk')]
 filein = sys.argv[2] # meta1_edit
 fileout = sys.argv[3] # 
 
 with codecs.open(filein,"r","utf-8") as f:
  lines = [x.rstrip('\r\n') for x in f]
  print(len(lines),"lines read from",filein)

 newlines = convert(lines,opt1,opt2)
 write(fileout,newlines)
 if opt1 == 'hk':
  check_as(lines)
  
 
