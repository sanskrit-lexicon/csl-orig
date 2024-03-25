
------------------------------------------------------------
02-20-2024
redo.sh regnerates ../pw_hwextra.txt from ../pw.txt
Three steps:
python multik2.py ../pw.txt multik2.txt
python multik2a.py multik2.txt multik2a.txt
python make_hwextra.py multik2a.txt ../pw_hwextra.txt


-----------------------------------------------------
Notes on each step
---------------------
python multik2.py ../pw.txt multik2.txt
Examine the k2 field of each metaline.
For a k2 field with a ',' output a tab-delimited line with 5 values:
 L0 - L value of current entry
 L1 - L value of next entry
 pc - pc value of current entry
 k1 - k1 value of current entry
 k2 - k2 value of current entry
These are the ingredients for constructing the extra headword entries
--------------------------------------------

python multik2a.py multik2.txt multik2a.txt

multik2a.txt
For each line X of multik2.txt, note the k1 field and analyze the k2 field.
 - split k2 by ', ' There should be 2 or more pieces.
   for this discussion, assume there are 2 pieces k2a and k2b.
Each piece should have 1 of two forms:
  h. K2  (where h is a digit sequence) -- h is a homonym number
  K2
 Now we analyze each K2 and construct a K1 (see below)
 Check that the K1 for the first piece agrees with the k1 field of X.

Constructing K1 from K2. This is 'tricky'!
The technique used is to exclude
  all characters in K2 that are not slp1
  also slp1 accents and spaces excluded
   "aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL|~"


------------------------------------------------------------
python make_hwextra.py multik2a.txt ../pw_hwextra.txt


------------------------------------------------------------
; 06-29-2023
Ref: https://github.com/sanskrit-lexicon/PW/issues/32#issuecomment-1612416266
additional corrections in ../change_9b.txt
  at L=3458 and 7174
python ../updateByLine.py ../temp_pwab_9a.txt ../change_9b.txt ../temp_pwab_9b.txt
8 change transactions from change_9b.txt

cp ../temp_pwab_9b.txt ../temp_pwab_9.txt

python multik2.py ../temp_pwab_9b.txt multik2.txt
894 records written to multik2.txt

python multik2a.py multik2.txt multik2a.txt

python make_hwextra.py multik2a.txt ../pw_hwextra.txt

------------------------------------------------------------
------------------------------------------------------------
