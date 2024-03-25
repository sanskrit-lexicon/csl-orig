dictlo='pw'
echo "BEGIN: remake ../${dictlo}_hwextra.txt from ../${dictlo}.txt"
echo "remake multik2.txt from ../${dictlo}.txt"
python multik2.py ../${dictlo}.txt multik2.txt
echo "remake multik2a.txt from multik2.txt"
python multik2a.py multik2.txt multik2a.txt
echo "remake ../${dictlo}_hwextra.txt from multik2a.txt"
python make_hwextra.py multik2a.txt ../${dictlo}_hwextra.txt
echo "END: remake ../${dictlo}_hwextra.txt from ../${dictlo}.txt"
