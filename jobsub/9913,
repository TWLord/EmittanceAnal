#!/bin/bash 

. /storage/epp2/phumhf/MICE/maus--versions/MAUSv3.3.2/env.sh 
cd /storage/epp2/phumhf/MICE/maus--versions/MAUSv3.3.2/bin/user/first-observation-paper-scripts 

mytempdir="$(mktemp -d)"
cd $mytempdir
echo "Making temp dir $mytempdir "

echo " ---- Copying root files for analysis ---- "
echo cp /storage/epp2/mice/phumhf/ReconData/MAUSv3.3.2/9907, 9908, 9909, 9912, 9913, 9914, /*.root $mytempdir/
cp /storage/epp2/mice/phumhf/ReconData/MAUSv3.3.2/9907, 9908, 9909, 9912, 9913, 9914, /*.root $mytempdir/

sed -i "s%.*a_file = .*%        a_file = \"$mytempdir\/\*_sim.root\"%" /storage/epp2/phumhf/MICE/EmittanceAnal/config/c2/movedata/config_2_9907, 9908, 9909, 9912, 9913, 9914, _full.py

echo "Copied files : "
echo "$(ls)"

cd /storage/epp2/phumhf/MICE/maus--versions/MAUSv3.3.2/bin/user/first-observation-paper-scripts 

PYTHONPATH=$PYTHONPATH:/storage/epp2/phumhf/MICE/EmittanceAnal
echo $PYTHONPATH
python /storage/epp2/phumhf/MICE/EmittanceAnal/bin/run_one_analysis.py config/c2/movedata/config_2_9907, 9908, 9909, 9912, 9913, 9914, _full.py

