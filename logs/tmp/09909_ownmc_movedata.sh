#!/bin/bash 

. /storage/epp2/phumhf/MICE/maus--versions/MAUSv3.3.2/env.sh 
cd /storage/epp2/phumhf/MICE/maus--versions/MAUSv3.3.2/bin/user/first-observation-paper-scripts 

mytempdir="$(mktemp -d)"
cd $mytempdir
echo "Making temp dir $mytempdir "

echo " ---- Copying root files for analysis ---- "
echo cp /storage/epp2/mice/phumhf/analMC/09909_v2/*//*.root $mytempdir/
cp /storage/epp2/mice/phumhf/analMC/09909_v2/*//*.root $mytempdir/

sed -i "s%.*a_file = .*%        a_file = \"$mytempdir\/\*.root\"%" /storage/epp2/phumhf/MICE/EmittanceAnal/config/c4/movedata/config_4_9909_full.py

echo "Copied files : "
echo "$(ls)"

cd /storage/epp2/phumhf/MICE/maus--versions/MAUSv3.3.2/bin/user/first-observation-paper-scripts 

PYTHONPATH=$PYTHONPATH:/storage/epp2/phumhf/MICE/EmittanceAnal
echo $PYTHONPATH
python /storage/epp2/phumhf/MICE/EmittanceAnal/bin/run_one_analysis.py config/c4/movedata/config_4_9909_full.py

