#!/bin/bash

#var=1-6
#var=5

queue="xxl"
#queue="short"

#Type="DATA"
#Type="MC"
Type="AngMomCorr"

configdir="config/testing${Type}"


#for var in "v201" ; do
#for var in "v30" ; do
#for var in "v30" "v201" ; do
#for var in "v301" ; do
#for var in "v40" "v40short" ; do
#for var in "v43" ; do
for var in "v43_testrecalcCorr" ; do
#for var in "vReco" "vRecoNew" "vReco100mmBz" ; do
    #for run in "9909" ; do
    #for run in "9910" "9911" ; do
    #for run in "9909" "9910" "9911" ; do
    #for run in "9911" ; do
    #for run in "9911" "9885" "9763" ; do
    #for run in "9911" "9885" ; do
    for run in "9885" ; do
    #for run in "9763" ; do
    #for run in "10318" ; do # 6-140
    #for run in "10318" "9911" "9885" "9763" ; do
    #for run in "10318" "10509" ; do # 6-140
    #for run in "10317" "10504" ; do # 4-140
    #for run in "10318" "10317" "10509" "10504" ; do

bsub -q $queue -G micegrp -M 20000 -oo /home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/logs/0${run}_AngMomCorr${var}${Type}.log "cd /home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/ ; . ../../../env.sh ; python bin/run_one_analysis.py ${configdir}/config_4_${run}_${var}.py ; echo $var,$Type"

done
done
