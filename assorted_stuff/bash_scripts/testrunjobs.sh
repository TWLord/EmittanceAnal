#!/bin/bash

#var=1-6
#var=5

queue="xxl"
#queue="short"

#Type="DATA"
Type="MC"

configdir="config/testing${Type}"


#configdir="config/testingMC"
#configdir="config/testingDATA"

#for var in "" "2" "3" "4" "5" "6" "7" "8" "9" "10" "11" "12" "13" "14" "15" "16" "17" "18" "19" "20" "pt0" "pt1" "pt2" "pt3" "pt4" "pt5" "pt6" "pt7" "pt8" "pt9" "pt10"  ; do
#for var in "" ; do
#for var in "" "2" ; do
#for var in "2" ; do
#for var in 9 10 ; do
#for var in 11 12 13 14 ; do
#for var in 13 ; do
#for var in 15 ; do
#for var in 2 3 4 ; do
#for var in 2 3 4 5 6 7 8 ; do
#for var in 3 5 6 7 8 ; do
#for var in 0 ; do
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
#for var in "half" "all" ; do
#for var in "half3" ; do
#for var in "3" "half3" ; do
#for var in "3" "half3" "all3" ; do
#for var in "half3cheat" ; do
#for var in "half3cheat2" ; do
#for var in "half3cheat2_noap" ; do
#for var in "half3cheat3" ; do
#for var in "half3cheat" "half3cheat2" ; do
#for var in "half3cheat4" "half3cheat4_noap" ; do
#for var in "half3cheat5" "half3cheat5_noap" ; do
#for var in "half3cheat6" "half3cheat6_noap" ; do
#for var in "half3cheat7" "half3cheat7_noap" "half3cheat8" "half3cheat8_noap" ; do
#for var in "half3cheat9" "half3cheat9_noap" ; do
#for var in "half3cheat11" ; do
#for var in "4" ; do
#for var in "5" ; do
#for var in "6" ; do
#for var in "7" ; do
#for var in "8" ; do
#for var in "4" "5" ; do
#for var in "4" "5" "6" "7" "8" "9" "10" "11" ; do
#for var in "8" "9" "10" "11" ; do
#for var in "OwnMC1" ; do
for var in "Sys1" ; do
#for var in "all3" ; do
#for var in "all" ; do
#for var in "fast" ; do
#for var in "fast" "fast2" ; do
#for var in "fast3" ; do
#for var in "fast4" ; do
#for var in "fast5" ; do
#for var in "fast6" ; do
#for var in "fast7" ; do
#for var in "fast8" "fast9" "fast10" "fast11" ; do
    #for run in "9909" ; do
    #for run in "9910" "9911" ; do
    #for run in "9909" "9910" "9911" ; do
    #for run in "10318" ; do # 6-140
    for run in "9883" ; do # 3-140
    #for run in "10318" "10509" ; do # 6-140
    #for run in "10317" "10504" ; do # 4-140
    #for run in "10318" "10317" "10509" "10504" ; do

bsub -q $queue -G micegrp -M 20000 -oo /home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/logs/0${run}_mcspilltest${var}${Type}.log "cd /home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/ ; . ../../../env.sh ; python bin/run_one_analysis.py ${configdir}/config_3_${run}_test${var}.py ; echo $var,$Type"

done
done
