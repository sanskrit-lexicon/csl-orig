import sys,re,codecs
sys.stdout.reconfigure(encoding='utf-8') 

if __name__=="__main__":
 filein = sys.argv[1] #  xxx.txt (path to digitization of xxx)
 fileout = sys.argv[2] # extended ascii
 
 with codecs.open(filein,"r","cp1252") as f:
  with codecs.open(fileout,"w","utf-8") as fout:
   for x in f:
    x = x.rstrip('\r\n')
    out = x+'\n'
    try:
     fout.write(out)
    except:
     print('problem:',x)
"""
problem: Ā  (\u0100)  1279 := LATIN CAPITAL LETTER A WITH MACRON
problem: ā  (\u0101) 16422 := LATIN SMALL LETTER A WITH MACRON
problem: Ī  (\u012a)    22 := LATIN CAPITAL LETTER I WITH MACRON
problem: ī  (\u012b)  2143 := LATIN SMALL LETTER I WITH MACRON
problem: Ś  (\u015a)  8459 := LATIN CAPITAL LETTER S WITH ACUTE
problem: ś  (\u015b)  1467 := LATIN SMALL LETTER S WITH ACUTE
problem: Ū  (\u016a)     4 := LATIN CAPITAL LETTER U WITH MACRON
problem: ū  (\u016b)   672 := LATIN SMALL LETTER U WITH MACRON
problem: ȧ  (\u0227)     1 := LATIN SMALL LETTER A WITH DOT ABOVE
problem: ˘  (\u02d8)     1 := BREVE
problem: Ḍ  (\u1e0c)     2 := LATIN CAPITAL LETTER D WITH DOT BELOW
problem: ḍ  (\u1e0d)   478 := LATIN SMALL LETTER D WITH DOT BELOW
problem: ṃ  (\u1e43)   204 := LATIN SMALL LETTER M WITH DOT BELOW
problem: ṅ  (\u1e45)   584 := LATIN SMALL LETTER N WITH DOT ABOVE
problem: ṇ  (\u1e47)  4317 := LATIN SMALL LETTER N WITH DOT BELOW
problem: Ṛ  (\u1e5a)   396 := LATIN CAPITAL LETTER R WITH DOT BELOW
problem: ṛ  (\u1e5b)  1243 := LATIN SMALL LETTER R WITH DOT BELOW
problem: Ṣ  (\u1e62)     4 := LATIN CAPITAL LETTER S WITH DOT BELOW
problem: ṣ  (\u1e63)  2899 := LATIN SMALL LETTER S WITH DOT BELOW
problem: Ṭ  (\u1e6c)     1 := LATIN CAPITAL LETTER T WITH DOT BELOW
problem: ṭ  (\u1e6d)   571 := LATIN SMALL LETTER T WITH DOT BELOW
problem: 卐  (\u5350)     1 := CJK UNIFIED IDEOGRAPH-5350
"""
