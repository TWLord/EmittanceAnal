#!/bin/bash

here=/vols/mice/tlord1/EmittanceAnal
#MAUSdir=~/MICE/maus--versions/MAUSv3.3.2
MAUSdir=/vols/mice/tlord1/maus--versions/MAUSv3.3.2
DATApath=/vols/mice/tlord1

TIME="48:00:00"
#TIME="96:00:00"

ABS=$1
opt=$2
VERSION=$3

templatedir=config/solenoid/2017-02-6/ABS-TEMPLATE/

rn="${opt%,*}"
if [ ! -z "$rn" ] ; then 

Optics="${opt##*,}"
echo $rn
echo $Optics
#_runs="${runs//, /_}"
#echo $_runs

#Optics=3-140

if [ $rn -lt 10000 ] ; then
runnumber=0$rn
else 
runnumber=$rn
fi
rn=$rn

datadir=${DATApath}/MC/MAUSv3.3.2/$runnumber$VERSION

configdir=config/movedata/runs/$rn

if [ ! -e $here/$configdir/config_3_${rn}_full.py  ] ; then

echo "Missing config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/OfficialMC_full/OfficialMC_movedata/g" -e "s/ABS/$ABS/g" -e "s/VERSION/$VERSION/g" $here/$templatedir/config_3_${Optics}.py > $here/$configdir/config_3_${rn}_full.py

else 
echo "Running config for run $rn"
fi
echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


#mytempdir=\"\$(mktemp -d)\"
#cd \$mytempdir
#echo \"Making temp dir \$mytempdir \"

cd \$TMPDIR
echo \"Running from temp dir \$TMPDIR \"


echo \" ---- Copying root files for analysis ---- \"
echo cp $datadir/*.root \$TMPDIR/
cp $datadir/*.root \$TMPDIR/

sed -i \"s%.*a_file = .*%        a_file = \\\"\$TMPDIR\/\\*_sim.root\\\"%\" $here/$configdir/config_3_${rn}_full.py

echo \"Copied files : \"
echo \"\$(ls)\"

#cd $here
cp $configdir/config_3_${rn}_full.py \$TMPDIR/ 

PYTHONPATH=\$PYTHONPATH:$here
echo \$PYTHONPATH
#python $here/bin/run_one_analysis.py $configdir/config_3_${rn}_full.py

python $here/bin/run_one_analysis.py config_3_${rn}_full.py

" \
| tee $here/logs/tmp/run_${runnumber}_mc_movedata.sh
chmod +x $here/logs/tmp/run_${runnumber}_mc_movedata.sh

qsub -l h_rt=$TIME -q hep.q -wd $here/logs/ $here/logs/tmp/run_${runnumber}_mc_movedata.sh

else
echo "no runs for $opt"
fi
