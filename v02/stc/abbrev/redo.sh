echo "remake temp_updateByLine.txt"
python abbrev.py temp_old_stc.txt abbreviationsStchoupak.txt manualByLine.txt temp_updateByLine.txt
echo "remake temp_new_stc.txt"
python updateByLine.py temp_old_stc.txt temp_updateByLine.txt temp_new_stc.txt
echo "When temp_new_stc.txt is ready,remake ../stc.txt by"
echo "copying temp_new_stc.txt  to ../stc.txt"
# cp temp_new_stc.txt ../stc.txt
