dictlo=$1 # assume lower case
dictup=${dictlo^^}  # upper case
cd ../  # to toplevel csl-orig
mkdir $dictlo
origdir="v00/csl-data/${dictup}Scan/2020/orig"
mv $origdir/${dictlo}.txt $dictlo/
mv $origdir/hwextra/${dictlo}_hwextra.txt $dictlo/

