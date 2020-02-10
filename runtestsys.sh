#!/bin/bash

for i in `seq 0 19` ; do

bsub -G micegrp -M 20000 -oo ~/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/config/testingsys/log/testsys${i}.log "cd ~/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts; . ../../../env.sh; python bin/run_one_analysis.py config/testingsys/config_7_10509_tku_density_plus${i}.py"

done
