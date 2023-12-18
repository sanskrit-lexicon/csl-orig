
------------------------------------------------------------
12-18-2023
redo.sh regnerates ../pwkvn_hwextra.txt from ../pwkvn.txt
-----------------------------------------------------
python multik2.py ../pwkvn.txt multik2.txt
90460 lines read from ../pwkvn.txt
22611 entries found
1500 metalines with comma
1500 records written to multik2.txt


--------------------------------------------
multik2a.txt
# construct k1 for each k2.
# check that 1st k1 agrees with k1 of metaline.
python multik2a.py multik2.txt multik2a.txt

parse_k2 error: k2="Animila (?)",
line=2615       2616    2-293-c AnandagirIya    AnandagirIya, AnandatARqavavarRana, AnandatAratamyaKaRqana, Anandatilaka, AnandatIrTIya, AnandarAGava, AnandavarD
Iya, AnandavilAsa, AnandasAgarastava, AnandasAratAratamyaKaRqana, Animila (?)

parse_k2 error: k2="avivekam (!)",
line=3955       3956    3-254-b avivekam        avivekam (!), avivecam

parse_k2s error: rec.k1=avivekam, rec.k1s[0]=(!)
line=3955       3956    3-254-b avivekam        avivekam (!), avivecam

parse_k2s error: rec.k1=arcatrya, rec.k1s[0]=(arcatrya)
line=6425       6426    5-245-a arcatrya        (arcatrya), arcatri/a

parse_k2 error: k2="auch *indindira",
line=6836       6837    5-249-c indindirA       indindirA, auch *indindira

parse_k2 error: k2="richtig kavacahara",
line=7024       7025    5-251-c kavacaDara      kavacaDara, richtig kavacahara

parse_k2s error: rec.k1=aRi, rec.k1s[0]=(aRi)
line=10010      10011   7-292-c aRi     (aRi), aRI

parse_k2s error: rec.k1=apahft, rec.k1s[0]=°apahft
line=11813      11814   7-303-c apahft  °apahft, apahelana

parse_k2s error: rec.k1=AkarRatawa, rec.k1s[0]=AkarRatawa°
line=13837      13838   7-316-b AkarRatawa      AkarRatawa°, AkarRadeSAntam, °AkarRin

parse_k2s error: rec.k1=AbrahmARqa, rec.k1s[0]=AbrahmARqa°
line=14206      14207   7-318-d AbrahmARqa      AbrahmARqa°, ABaraRI

parse_k2s error: rec.k1=CandombuDi, rec.k1s[0]=Cando'mbuDi
line=17412      17413   7-342-b CandombuDi      Cando'mbuDi, CandoratnahalAyuDa, Candoviveka

1500 records written to multik2a.txt
2365 extra headwords

NOTE: make changes to ../pwkvn.txt that 'solve' the above 'errors'/

RERUN:
python multik2.py ../pwkvn.txt multik2.txt
90460 lines read from ../pwkvn.txt
22611 entries found
1500 metalines with comma
1500 records written to multik2.txt

python multik2a.py multik2.txt multik2a.txt
1500 records written to multik2a.txt
2365 extra headwords


------------------------------------------------------------
python make_hwextra.py multik2a.txt ../pwkvn_hwextra.txt
2365 records written to ../pwkvn_hwextra.txt


------------------------------------------------------------
; 06-29-2023
Ref: https://github.com/sanskrit-lexicon/PWKVN/issues/32#issuecomment-1612416266
additional corrections in ../change_9b.txt
  at L=3458 and 7174
python ../updateByLine.py ../temp_pwkvnab_9a.txt ../change_9b.txt ../temp_pwkvnab_9b.txt
8 change transactions from change_9b.txt

cp ../temp_pwkvnab_9b.txt ../temp_pwkvnab_9.txt

python multik2.py ../temp_pwkvnab_9b.txt multik2.txt
894 records written to multik2.txt

python multik2a.py multik2.txt multik2a.txt

python make_hwextra.py multik2a.txt ../pwkvn_hwextra.txt

------------------------------------------------------------
------------------------------------------------------------
