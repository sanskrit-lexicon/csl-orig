08-25-2024
 gra_hwextra.txt latest copy, previously in gra directory.
 The version in gra directory is empty file, but still needed for
 redo_hw.sh in csl-pywork/v02.
------------------------------------------------------------
12-14-2023
redo.sh regnerates ../gra_hwextra.txt from ../gra.txt
-----------------------------------------------------
python multik2.py ../gra.txt multik2.txt
89074 lines read from ../gra.txt
11871 entries found
894 metalines with comma
894 records written to multik2.txt
--------------------------------------------
multik2a.txt
# construct k1 for each k2.
# check that 1st k1 agrees with k1 of metaline.
python multik2a.py multik2.txt multik2a.txt

generate_Ls_manual: 6754.1,6755,1 -> ['6754.2']
generate_Ls_manual: 6881,6881.5,1 -> ['6881.1']
896 records written to multik2a.txt
916 extra headwords


------------------------------------------------------------
python make_hwextra.py multik2a.txt ../gra_hwextra.txt


------------------------------------------------------------
; 06-29-2023
Ref: https://github.com/sanskrit-lexicon/GRA/issues/32#issuecomment-1612416266
additional corrections in ../change_9b.txt
  at L=3458 and 7174
python ../updateByLine.py ../temp_graab_9a.txt ../change_9b.txt ../temp_graab_9b.txt
8 change transactions from change_9b.txt

cp ../temp_graab_9b.txt ../temp_graab_9.txt

python multik2.py ../temp_graab_9b.txt multik2.txt
894 records written to multik2.txt

python multik2a.py multik2.txt multik2a.txt

python make_hwextra.py multik2a.txt ../gra_hwextra.txt

------------------------------------------------------------
------------------------------------------------------------
