#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

#here=/home/phumhf/MICE/maus--versions/newThirdPartyMAUSv3.3.2/bin/user/first-observation-paper-scripts
#MAUSdir=~/MICE/maus--versions/newThirdPartyMAUSv3.3.2


queue=medium
#queue=long
#queue=xlong

#config_2_reco_nostat+corr
#config_3_mc_reco
#config_4_mc_reco
#config_testing_4_mc_reco
#config_5_reco_stat+corr
#config_2_multitest_reco_nostat+corr

#"config_3_OfficialMC+tofcuts_mc_reco"
#"config_5_OfficialMC_9885_reco_stat+corr"

#for configfile in "config_3_OfficialMC_mc_reco" ; do
#for configfile in "config_3_OfficialMC_test" "config_3_OfficialMC_test2" "config_3_OfficialMC+tofcuts_mc_reco_full" ; do
#for configfile in "config_3_OfficialMC+tofcuts_mc_reco_full"; do
#for configfile in "config_3_OfficialMC+tofcuts_mc_reco"; do
#for configfile in "errortestamp" "errortestdensity" "errortestdensityrogers" "errortestextrapolation" "errortestglobals" "errortestoptics" "errortestplots" ; do
#for configfile in "errortestampfull" ; do

#for configfile in "config_2_9883_full" "config_2_9885_full" "config_2_9886_full" ; do
#for configfile in "config_3_OfficialMC_9885_full" ; do 
#for configfile in "config_0_quicktestMC" "config_0_quicktestMC2" ; do 
for configfile in "config_0_quicktestMC2" ; do 
#for configfile in "config_3_OfficialMC_9883_full" "config_3_OfficialMC_9885_full" "config_3_OfficialMC_9886_full" ; do 
#for configfile in "config_3_OfficialMC_9883_full" "config_3_OfficialMC_9886_full" ; do 
#for configfile in "config_5_OfficialMC_9883_reco_stat+corr" "config_5_OfficialMC_9885_reco_stat+corr" "config_5_OfficialMC_9886_reco_stat+corr" ; do 
#for configfile in "config_5_OfficialMC_9883_reco_stat+corr" "config_5_OfficialMC_9886_reco_stat+corr" ; do 
#for configfile in "config_5_OfficialMC_9883_reco_stat+corr_amp" "config_5_OfficialMC_9885_reco_stat+corr_amp" "config_5_OfficialMC_9886_reco_stat+corr_amp" ; do 
#for configfile in "config_5_OfficialMC_9883_reco_stat+corr_amp_1000spills" "config_5_OfficialMC_9885_reco_stat+corr_amp_1000spills" "config_5_OfficialMC_9886_reco_stat+corr_amp_1000spills" ; do 
#for configfile in "config_5_OfficialMC_9883_reco_stat+corr_amp_2000spills" "config_5_OfficialMC_9885_reco_stat+corr_amp_2000spills" "config_5_OfficialMC_9886_reco_stat+corr_amp_2000spills" ; do 
#for configfile in "config_5_OfficialMC_9885_reco_stat+corr" ; do 

echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 

python bin/run_one_analysis.py config/${configfile}.py

#python bin/run_one_analysis.py config/config_5_OfficialMC_9885_reco_stat+corr.py
" \
| tee $here/logs/tmp/${configfile}.sh
chmod +x $here/logs/tmp/${configfile}.sh
bsub -G micegrp -M 16000 -oo $here/logs/${configfile}.log -q ${queue} $here/logs/tmp/${configfile}.sh
#bsub -G micegrp -M 16000 -eo $here/logs/${configfile}.error -oo $here/logs/${configfile}.log -q ${queue} $here/logs/tmp/${configfile}.sh
done
