
11-04-2019
This describes a reorganization of the csl-orig repository.
For each dictionary xxx, there are two important data files:
xxx.txt  (the Cologne digitization)
xxx_hwextra.txt  (extra and/or alternate headwords)

Before the reorg,  the paths to these files are:
v00/csl-data/XXXScan/2020/orig/xxx.txt
v00/csl-data/XXXScan/2020/orig/hwextra/xxx_hwextra.txt

After the reorg, the paths will be
xxx/xxx.txt
xxx/xxx_hwextra.txt

And the v00 directory will be absent.

This reorg was discussed in https://github.com/sanskrit-lexicon/csl-pywork/issues/7.

The reorg is done in steps:

bash reorg1.sh xxx
  This creates csl-orig/xxx directory and
  moves xxx.txt and xxx_hwextra.txt to the new directory.
bash reorg1_all.sh
  This script runs `sh reorg1.sh xxx` for all dictionaries xxx.

Miscellaneous other changes (current directory is csl-orig/reorg)
mv ../v00/csl-data/MW72Scan/2020/orig/20191029-greek ../mw72/
mv ../v00/updateDistinctData.sh .
   This is the script used to initialize first form of this repository.

Remove v00
rm -r ../v00


Change of mind:  keep all the xxx directories in csl-orig/v02
keep v00 at top level, with just the initialization script:
  updateDistinctData
