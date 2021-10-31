#!/bin/bash

queue="xxl"
#queue="short"

#Type="DATA"
#Type="MC"
Type="AngMomSys"

configdir="config/testing${Type}"


for sys in "tkd_density_plus" "tkd_scale_C_plus" "tku_base" "tku_density_plus" "tku_scale_C_plus" "tkd_pos_plus" "tkd_scale_E1_plus" "tku_base_tkd_chi2_threshold" "tku_pos_plus" "tku_scale_E1_plus" "tkd_rot_plus" "tkd_scale_E2_plus" "tku_base_tkd_fiducial_radius" "tku_rot_plus" "tku_scale_E2_plus" ; do 
    #for run in "9909" ; do
    #for run in "9910" "9911" ; do
    #for run in "9909" "9910" "9911" ; do
    #for run in "9911" ; do
    #for run in "9911" "9885" "9763" ; do
    #for run in "9911" "9885" ; do
    for run in "9883" ; do
    #for run in "9763" ; do
    #for run in "10318" ; do # 6-140
    #for run in "10318" "9911" "9885" "9763" ; do
    #for run in "10318" "10509" ; do # 6-140
    #for run in "10317" "10504" ; do # 4-140
    #for run in "10318" "10317" "10509" "10504" ; do

bsub -q $queue -G micegrp -M 20000 -oo /home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/logs/${run}_AngMomSys${sys}.log "cd /home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/ ; . ../../../env.sh ; python bin/run_one_analysis.py ${configdir}/config_7_${run}_full_${sys}.py ; echo $sys"

done
done
