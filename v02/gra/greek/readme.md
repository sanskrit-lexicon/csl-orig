The Vedaweb project at Cologne (https://vedaweb.uni-koeln.de/) has added Greek text to Grassman dictionary.
This subdirectory devoted to importing these into gra.txt.

Francisco Mondaca (https://github.com/vocabulista) from VedaWeb
provided the file 'entries_with_gr_tags_filled_1.txt'.


## entries_with_gr_tags_filled_1.txt  186 cases, 1 per line
Attachment from Francisco Mondaca.
187 lines.
Samples:
```
lemma_akzu_58	ἀγρεύω, ἄγρευμα, ἄγρηνον
lemma_Sam_8658	κάμ-νω
lemma_sU_10078	σεύω (ἐσσύμενος); υἱός
```
## entries Format:
2 tab delimited fields:
- lemma_hw_id    
  * hw = SLP1 spelling 
  * id = sequence number
     * Note: It appears to be 1 less than the L-number in current gra.txt
     e.g., akzu 58 : the L-num of akzu in gra.txt is 59
     The last line is lemma_hiruk_10709, and Lnum of hiruk is 10710.
- Greek.  
  * one or more greek words.  
    - Sometimes a ',' example 
    - lemma_akzu_58	ἀγρεύω, ἄγρευμα, ἄγρηνον
    - By scan, these three words are sequential, with separating commas.
    There is only one `<lang n="greek"></lang>` in gra.txt.
  * Sometimese a ';' example:
    `lemma_agra_100	ἄγω, ἀγός, ἄκτωρ; ἡγεῖσθαι, στρατ-ηγός`
    in gra.txt there are TWO greek texts.  So the ';' is an instance separator.
## temp_old_gra.txt
 cp ../gra.txt temp_old_gra.txt
This uses gra.txt of commit 079c8c65a8f2148cfdca7a8bcea4618f577c104f
## Hebrew:
lemma_naqa_4811	νάρδος; נֵרְדְּ
## One addition to entries:
lemma_dA_4163  ἔδω-ν

## updateByLine.txt - made bu greek_changes.py
python greek_changes.py temp_old_gra.txt entries_with_gr_tags_filled_1.txt updateByLine.txt

## temp_new_gra.txt
python updateByLine.py temp_old_gra.txt updateByLine.txt temp_new_gra.txt
## Lastly, replace gra.txt by temp_new_gra.txt and sync to github
cp temp_new_gra.txt ../gra.txt
## Tasks in other repositories
`<lang n="hebrew">...</lang>` is a new attribute value for the lang tag.

Change csl-pywork/v02/makotemplates/pywork/one.dtd accordingly.

Then remake gra.
