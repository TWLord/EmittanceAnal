#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

#queue=medium
queue=xlong

#for runnumber in 9883 9886; do 
#for runnumber in 10249 9888 9889; do 
for runnumber in 9911; do 

configdir=config/runs/$runnumber

echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_2_${runnumber}_full.py

" \
| tee $here/logs/tmp/${runnumber}_reco.sh
chmod +x $here/logs/tmp/${runnumber}_reco.sh
bsub -G micegrp -M 6000 -oo $here/logs/${runnumber}_reco.log -q ${queue} $here/logs/tmp/${runnumber}_reco.sh
#bsub -G micegrp -M 6000 -eo $here/logs/${runnumber}_reco.error -oo $here/logs/${runnumber}_reco.log -q ${queue} $here/logs/tmp/${runnumber}_reco.sh
done
