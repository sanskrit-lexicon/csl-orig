echo "BEGIN convert abch1.txt to version temp_abch.txt"
echo "temp_abch0.txt intermediate slp1 version"
python convert.py deva,slp1 abch1.txt temp_abch0.txt
echo "check invertability"
python convert.py slp1,deva temp_abch0.txt temp_abch0_deva.txt
echo "count of lines in diff should be 0"
diff abch1.txt temp_abch0_deva.txt | wc -l
echo ""
# Additional changes
echo ""
python addinfo.py temp_abch0.txt temp_abch.txt
echo "END convert abch1.txt to version temp_abch.txt"
echo "Do you want to copy temp_abch.txt to ../abch.txt  ?"

