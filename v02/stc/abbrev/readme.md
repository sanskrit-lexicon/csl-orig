This subdirectory devoted to adding common abbreviation markup for
STC dictionary.

A list of these common abbreviations appears in the [front matter](https://www.sanskrit-lexicon.uni-koeln.de/scans/csldev/csldoc/build/dictionaries/prefaces/stcpref/stcpref04.html).

Odile Caujolle transcribed this; her result is in this [pdf](abbreviationsStchoupak.pdf).

The pdf was converted to text file abbreviationsStchoupak.txt, and then
edited.  In this text file, lines beginning with semicolons are comments.
Each abbreviation appears on a non-commented line, with the abbreviation
separated from the 'abbreviation definition' by a tab character.
.
## temp_old_stc.txt
```
cp ../stc.txt temp_old_stc.txt
```
This uses stc.txt of commit 2ee76ba8819aa85040fcc38598a22e49cad73ba5

## temp_updateByLine.txt 
For each abbreviation X in abbreviationsStchoupak.txt, 
change `X` to `<ab>X</ab>` for each instance of X in the digitization.
There are several details of this substitution that guard against 
introduction of false positives.
The result is a list of digitization change transactions kept in file
temp_updateByLine.txt.
```
python abbrev.py temp_old_stc.txt abbreviationsStchoupak.txt manualByLine.txt temp_updateByLine.txt
```

## temp_new_stc.txt
The change transactions are applied to the old digitization, resulting in
a new version of the digitization.
```
python updateByLine.py temp_old_stc.txt temp_updateByLine.txt temp_new_stc.txt
```
## Lastly, replace stc.txt by temp_new_stc.txt and sync to github
```
cp temp_new_stc.txt ../stc.txt
```
## Tasks in other repositories

Change csl-pywork/v02/distinctfiles/stc/pywork/ by
 adding an stcab subdirectory. See the readme file therein

Also, see https://github.com/sanskrit-lexicon/COLOGNE/issues/298.
