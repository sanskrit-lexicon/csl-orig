echo "hwextra..."
python hwextra.py ../pwkvn.txt ../pwkvn_hwextra.txt
echo "pwkvn_hk.txt"
python final.py slp1,hk ../pwkvn.txt pwkvn_hk.txt
# check invertibility
python final.py hk,slp1 pwkvn_hk.txt temp_pwkvn.txt
diff ../pwkvn.txt temp_pwkvn.txt | wc -l

echo "pwkvn_hk_ansi.txt"
python utf8_cp1252.py pwkvn_hk.txt pwkvn_hk_ansi.txt
# check invertibility
python cp1252_utf8.py pwkvn_hk_ansi.txt temp.txt
diff pwkvn_hk.txt temp.txt | wc -l

echo "pwkvn_deva.txt"
python deva.py slp1,deva ../pwkvn.txt pwkvn_deva.txt
# check
python deva.py deva,slp1 pwkvn_deva.txt temp_pwkvn.txt
diff ../pwkvn.txt temp_pwkvn.txt | wc -l
