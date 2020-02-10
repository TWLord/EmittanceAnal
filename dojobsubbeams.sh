#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

queue=xlong

configdir=config/beams
#configfile=beams_2017-02-6_140
configfile=beams_2017-02-6_highmom

echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_${configfile}.py

" \
| tee $here/logs/tmp/${queue}_${configfile}.sh
chmod +x $here/logs/tmp/${queue}_${configfile}.sh
bsub -G micegrp -M 16000 -oo $here/logs/${queue}_${configfile}.log -q ${queue} $here/logs/tmp/${queue}_${configfile}.sh

