#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

#queue=xlong
queue=xxl

for runnumber in 9883 9886; do 
#for runnumber in 9883; do 
#for runnumber in 9886; do 

configdir=config/runs/$runnumber

echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_3_OfficialMC_${runnumber}_full.py

" \
| tee $here/logs/tmp/${runnumber}_mc.sh
chmod +x $here/logs/tmp/${runnumber}_mc.sh
bsub -G micegrp -M 16000 -oo $here/logs/${runnumber}_mc.log -q ${queue} $here/logs/tmp/${runnumber}_mc.sh
#bsub -G micegrp -M 16000 -eo $here/logs/${runnumber}_mc.error -oo $here/logs/${runnumber}_mc.log -q ${queue} $here/logs/tmp/${runnumber}_mc.sh
done
