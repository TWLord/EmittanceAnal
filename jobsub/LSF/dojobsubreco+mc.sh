#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

queue=xlong

#for runnumber in 9883 9885 9886; do 
for runnumber in 10243 10245 10246 10314 10317 10318 10319 10579 10580 10581 10582 9883 9885 9886; do 
#for runnumber in 9883; do 
#for runnumber in 9886; do 

configdir=config/runs/$runnumber

echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_3_OfficialMC_${runnumber}_full.py

python bin/run_one_analysis.py $configdir/config_5_OfficialMC_${runnumber}_reco_stat+corr.py

" \
| tee $here/logs/tmp/${runnumber}_mc+reco.sh
chmod +x $here/logs/tmp/${runnumber}_mc+reco.sh
bsub -G micegrp -M 16000 -oo $here/logs/${runnumber}_mc+reco.log -q ${queue} $here/logs/tmp/${runnumber}_mc+reco.sh
#bsub -G micegrp -M 16000 -eo $here/logs/${runnumber}_mc+reco.error -oo $here/logs/${runnumber}_mc+reco.log -q ${queue} $here/logs/tmp/${runnumber}_mc+reco.sh
done
