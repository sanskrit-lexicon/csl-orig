#!/bin/bash
echo "Download unique scripts to each dictionary's pywork from live Cologne server to distinctscripts folder."
scripts=(make_xml.py)
dicts=(ACC AE AP90 AP BEN BHS BOP BOR BUR CAE CCS GRA GST IEG INM KRM MCI MD MW72 MWE MW PD PE PGN PUI PWG PW SCH SHS SKD SNP STC VCP VEI WIL YAT)
for dict in ${dicts[*]}
do
	for script in ${scripts[*]}
	do
		echo "${dict,,}"
		mkdir -p csl-data/"$dict"Scan/2020/orig
		wget -O csl-data/"$dict"Scan/2020/orig/"${dict,,}".txt https://www.sanskrit-lexicon.uni-koeln.de/scans/"$dict"Scan/2014/orig/"${dict,,}".txt
	done
done

