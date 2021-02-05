#!/bin/bash

here=/storage/epp2/phumhf/MICE/EmittanceAnal
#MAUSdir=~/MICE/maus--versions/MAUSv3.3.2
MAUSdir=/storage/epp2/phumhf/MICE/maus--versions/MAUSv3.3.2
DATApath=/storage/epp2/mice/phumhf
#DATApath=/data/mice/phumhf

TIME="96:00:00"
#TIME="5760"
#TIME="34"
#TIME="5:00:00:00"
#TIME="UNLIMITED"

ABS="$1"
rn="$2"
runnumber="$3"
Optics="$4"
CC="$5"
VERSION="$6"
config="$7"
queue="$8"
templatedir="$9"
jobsuffix="${10}"
#datadir="$10"

echo $rn
echo $Optics

if [ $rn -lt 10000 ] ; then
runnumber=0$rn
else 
runnumber=$rn
fi
rn=$rn

if [ $config == "2" ] ; then
datadir=${DATApath}/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "3" ] ; then
datadir=${DATApath}/MC/MAUSv3.3.2/$runnumber$VERSION
elif [ $config == "4" ] ; then
datadir=${DATApath}/analMC/${runnumber}_$VERSION/*/
elif [ $config == "5" ] ; then
datadir=${DATApath}/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "6" ] ; then
datadir=${DATApath}/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "7" ] ; then
echo "[ERROR]: Shouldn't be running systematics from this script. Exiting.."
exit 1
elif [ $config == "8" ] ; then
datadir=${DATApath}/ReconData/MAUSv3.3.2/$runnumber
fi




#configdir=config/c$config/movedata
configdir=config/c$config/movedata/$VERSION

if [ ! -d $here/config/c$config ] ; then

echo "Making new parent directory $here/config/c$config/ "
mkdir -p $here/config/c$config
cp -f $here/$templatedir/__init__.py $here/config/c$config/
cp -f $here/$templatedir/__init__.py $here/config/c$config/movedata/
fi

if [ ! -e $here/$configdir/config_${config}_${rn}_full.py  ] ; then

echo "Missing config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" -e "s/CC/$CC/g" -e "s/VERSION/$VERSION/g" $here/$templatedir/config_${config}_${Optics}.py > $here/$configdir/config_${config}_${rn}_full.py

else 
echo "Running config for run $rn"
fi
echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 

mytempdir=\"\$(mktemp -d)\"
cd \$mytempdir
echo \"Making temp dir \$mytempdir \"

echo \" ---- Copying root files for analysis ---- \"
echo cp $datadir/*.root \$mytempdir/
cp $datadir/*.root \$mytempdir/

sed -i \"s%.*a_file = .*%        a_file = \\\"\$mytempdir\/\\*.root\\\"%\" $here/$configdir/config_${config}_${rn}_full.py

echo \"Copied files : \"
echo \"\$(ls)\"

cd $here 

PYTHONPATH=\$PYTHONPATH:$here
echo \$PYTHONPATH
python $here/bin/run_one_analysis.py $configdir/config_${config}_${rn}_full.py

" \
| tee $here/logs/tmp/${runnumber}_${jobsuffix}_movedata.sh
chmod +x $here/logs/tmp/${runnumber}_${jobsuffix}_movedata.sh
#bsub -G micegrp -M 20000 -oo $here/logs/${runnumber}_${jobsuffix}_movedata.log -q ${queue} $here/logs/tmp/${runnumber}_${jobsuffix}_movedata.sh

sbatch --mem 20000 -o $here/logs/${runnumber}_${jobsuffix}_movedata.log -p epp -t ${TIME} $here/logs/tmp/${runnumber}_${jobsuffix}_movedata.sh

