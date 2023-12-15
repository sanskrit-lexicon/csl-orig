echo "BEGIN: remake ../gra_hwextra.txt from ../gra.txt"
echo "remake multik2.txt from ../gra.txt"
python multik2.py ../gra.txt multik2.txt
echo "remake multik2a.txt from multik2.txt"
python multik2a.py multik2.txt multik2a.txt
echo "remake ../gra_hwextra.txt from multik2a.txt"
python make_hwextra.py multik2a.txt ../gra_hwextra.txt
echo "END: remake ../gra_hwextra.txt from ../gra.txt"
