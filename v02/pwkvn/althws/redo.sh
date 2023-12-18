echo "BEGIN: remake ../pwkvn_hwextra.txt from ../pwkvn.txt"
echo "remake multik2.txt from ../pwkvn.txt"
python multik2.py ../pwkvn.txt multik2.txt
echo "remake multik2a.txt from multik2.txt"
python multik2a.py multik2.txt multik2a.txt
echo "remake ../pwkvn_hwextra.txt from multik2a.txt"
python make_hwextra.py multik2a.txt ../pwkvn_hwextra.txt
echo "END: remake ../pwkvn_hwextra.txt from ../pwkvn.txt"
