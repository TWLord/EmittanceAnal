#!/bin/bash

here=/storage/epp2/phumhf/MICE/EmittanceAnal
MAUSdir=/storage/epp2/phumhf/MICE/maus--versions/MAUSv3.3.2

OldDATApath=/data/mice/phumhf
DATApath=/storage/epp2/mice/phumhf

TIME="96:00:00"

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
GEOPATH="${11}"
SYSTEMATIC="${12}"
SYSVERS="${13}"
#datadir="$12"

echo $rn
echo $Optics
echo "CC : $CC "
echo "VERSION : $VERSION "
echo "config : $config "
echo "queue : $queue "
echo "templatedir : $templatedir "
echo "jobsuffix: $jobsuffix "

#if [ $rn -lt 10000 ] ; then
#runnumber=0$rn
#else 
#runnumber=$rn
#fi
#rn=$rn

#if [ $config == "2" ] ; then
#datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
#elif [ $config == "3" ] ; then
#datadir=/data/mice/phumhf/MC/MAUSv3.3.2/$runnumber$VERSION
#elif [ $config == "4" ] ; then
#datadir=/data/mice/phumhf/analMC/${runnumber}_$VERSION/*/
#elif [ $config == "5" ] ; then
#datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
#elif [ $config == "6" ] ; then
#datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
#elif [ $config == "7" ] ; then
#echo "[ERROR]: Shouldn't be running systematics from this script. Exiting.."
#exit 1
#elif [ $config == "8" ] ; then
#datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
#fi


configdir=config/c$config

if [ ! -d $here/config/c$config ] ; then

echo "Making new parent directory $here/config/c$config/ "
mkdir -p $here/config/c$config
cp -f $here/$templatedir/__init__.py $here/config/c$config/
fi

if [ ! -e $here/$configdir/config_${config}_${rn}_full.py  ] ; then

echo "Missing config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${runnumber}/g" -e "s/ABS/$ABS/g" -e "s/CC/$CC/g" -e "s/VERSION/$VERSION/g" -e "s/SYSTEMATIC/$SYSTEMATIC/g" -e "s/SYSVERS/$SYSVERS/g" -e "s?GEOPATH?$GEOPATH?g" -e "s?$OldDATApath?$DATApath?g" $here/$templatedir/config_${config}_${Optics}.py > $here/$configdir/config_${config}_${rn}_full.py
#sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" -e "s/CC/$CC/g" -e "s/VERSION/$VERSION/g" -e "s/SYSTEMATIC/$SYSTEMATIC/g" -e "s/SYSVERS/$SYSVERS/g" $here/$templatedir/config_${config}_${Optics}.py > $here/$configdir/config_${config}_${rn}_full.py

else 
echo "Running config for run $rn"
fi
echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 

echo "No file movement"

cd $here

PYTHONPATH=\$PYTHONPATH:$here
echo \$PYTHONPATH
python $here/bin/run_one_analysis.py $configdir/config_${config}_${rn}_full.py

" \
| tee $here/logs/tmp/${rn}_${jobsuffix}.sh
chmod +x $here/logs/tmp/${rn}_${jobsuffix}.sh
#bsub -G micegrp -M 20000 -oo $here/logs/${rn}_${jobsuffix}.log -q ${queue} $here/logs/tmp/${rn}_${jobsuffix}.sh

#qsub -l h_rt=$TIME -q hep.q -wd $here/logs/ $here/logs/tmp/${rn}_${jobsuffix}.sh

sbatch --mem 20000 -o $here/logs/${rn}_${jobsuffix}.log -p epp -t ${TIME} $here/logs/tmp/${rn}_${jobsuffix}.sh
