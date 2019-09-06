#!/bin/bash

MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 

#python bin/run_one_analysis.py config/config_2_reco_nostat+corr.py
#python bin/run_one_analysis.py config/config_3_mc_reco.py
#python bin/run_one_analysis.py config/config_4_mc_reco.py
#python bin/run_one_analysis.py config/config_testing_4_mc_reco.py
#python bin/run_one_analysis.py config/config_5_reco_stat+corr.py

#python bin/run_one_analysis.py config/config_2_multitest_reco_nostat+corr.py
python bin/run_one_analysis.py config/config_3_OfficialMC+tofcuts_mc_reco.py
