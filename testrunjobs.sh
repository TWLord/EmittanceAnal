#!/bin/bash

#var=1-6
#var=5

configdir="config/testingMC"

#for var in "" "2" "3" "4" "5" "6" "7" "8" "9" "10" "11" "12" "13" "14" "15" "16" "17" "18" "19" "20" "pt0" "pt1" "pt2" "pt3" "pt4" "pt5" "pt6" "pt7" "pt8" "pt9" "pt10"  ; do
#for var in "" "2" ; do
#for var in 9 10 ; do
#for var in 11 12 13 14 ; do
#for var in 13 ; do
#for var in 15 ; do
#for var in 2 3 4 ; do
#for var in 2 3 4 5 6 7 8 ; do
#for var in 3 5 6 7 8 ; do
#for var in 2 ; do
#for var in 5 ; do
#for var in 16 17 18 19 20 ; do
#for var in "pt" ; do
#for var in "pt0" ; do
#for var in "" "pt0" ; do
#for var in "pt1" "pt2" "pt3" "pt4" "pt5" "pt6" ; do
#for var in "pt7" ; do
#for var in "pt8" ; do
#for var in "pt9" "pt10" ; do
#for var in "half2" ; do
#for var in "half" ; do
#for var in "all" ; do
#for var in "fast" ; do
#for var in "fast" "fast2" ; do
for var in "fast3" ; do
    #for run in "9909" ; do
    #for run in "9910" "9911" ; do
    for run in "9909" "9910" "9911" ; do

bsub -q xxl -G micegrp -M 20000 -oo /home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/logs/0${run}_mcspilltest${var}.log "cd /home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/ ; . ../../../env.sh ; python bin/run_one_analysis.py ${configdir}/config_3_${run}_test${var}.py "

done
done
