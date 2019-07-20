#!/bin/bash
echo "Download orig/xxx.txt to each dictionary's orig folder from live Cologne server to csl-data folder."

dictsthirteen=(BUR INM MWE PWG SKD STC)
dictsfourteen=(ACC AE AP90 AP BEN BHS BOP BOR CAE CCS GRA GST IEG KRM MCI MD MW72 MW PD PE PGN PUI PW SCH SHS SNP VCP VEI WIL YAT)
for dict in ${dictsthiteen[*]}
do
	echo "${dict,,}"
	mkdir -p csl-data/"$dict"Scan/2020/orig/hwextra
	#wget -O csl-data/"$dict"Scan/2020/orig/"${dict,,}".txt https://www.sanskrit-lexicon.uni-koeln.de/scans/"$dict"Scan/2013/orig/"${dict,,}".txt
	cp ../../../Cologne_localcopy/"${dict,,}"/pywork/hwextra/"${dict,,}"_hwextra.txt csl-data/"$dict"Scan/2020/orig/hwextra/"${dict,,}"_hwextra.txt
done

for dict in ${dictsfourteen[*]}
do
	echo "${dict,,}"
	mkdir -p csl-data/"$dict"Scan/2020/orig/hwextra
	# wget -O csl-data/"$dict"Scan/2020/orig/"${dict,,}".txt https://www.sanskrit-lexicon.uni-koeln.de/scans/"$dict"Scan/2014/orig/"${dict,,}".txt
	cp ../../../Cologne_localcopy/"${dict,,}"/pywork/hwextra/"${dict,,}"_hwextra.txt csl-data/"$dict"Scan/2020/orig/hwextra/"${dict,,}"_hwextra.txt
done

