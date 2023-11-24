अभिधानचिन्तामणि  by हेमचन्द्राचार्य
# --------------
# The base version is abch1.txt from Dhaval
sh redo.sh # generates abch.txt from abch1.txt
# this is what it does
# convert abch1.txt to slp1 version abch.txt
python convert.py deva,slp1 abch1.txt abch.txt
# check invertability
python convert.py slp1,deva abch.txt temp_abch1.txt
diff abch1.txt temp_abch1.txt
# should be no difference
rm temp_abch1.txt

# --------------
Notes on further steps:
# assume v4 as current directory
mkdir csl-orig/abch
cp prep/abch/abch.txt csl-orig/abch/abch.txt
touch csl-orig/abch/abch-meta2.txt
touch csl-orig/abch/abch_hwextra.txt
touch csl-orig/abch/abchheader.xml  # note this to be modified later

edit csl-pywork/dictparms.py
 # add info for abch
edit csl-pywork/inventory.txt
 # add info for abch
edit csl-pywork/redo_xampp_all.sh
edit csl-pywork/redo_cologne_all.sh

edit csl-websanlexicon/dictparms.py
 # add info for abch
mkdir csl-websanlexicon/distinctfiles/abch
mkdir csl-websanlexicon/distinctfiles/abch/web
mkdir csl-websanlexicon/distinctfiles/abch/web/webtc
echo "0001:pg_0001.pdf" >  csl-websanlexicon/distinctfiles/abch/web/webtc/pdffiles.txt

edit csl-pywork/makotemplates/pywork/hw.py
 add init_keys for abch

edit csl-pywork/makotemplates/pywork/redo_xml.sh
  SKIP abch1.xml
edit csl-pywork/makotemplates/pywork/make_xml.py
 construct_xmlstring_1 (for anhk)
 construct_xmlstring_2 (for abch)

gender-frequency list
python gender_list.py abch.txt gender_list.txt

