#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

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
SYSTEMATIC="${11}"
SYSFILE="${12}"
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




configdir=config/c$config/$VERSION

if [ ! -d $here/config/c$config ] ; then

echo "Making new parent directory $here/config/c$config/ "
mkdir -p $here/config/c$config
cp -f $here/$templatedir/__init__.py $here/config/c$config/
fi

if [ ! -e $here/$configdir/config_${config}_${rn}_full_${SYSTEMATIC}.py  ] ; then

echo "Missing config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" -e "s/CC/$CC/g" -e "s/VERSION/$VERSION/g" -e "s/SYSTEMATIC/$SYSTEMATIC/g" -e "s/SYSFILE/$SYSFILE/g" $here/$templatedir/config_${config}_${Optics}.py > $here/$configdir/config_${config}_${rn}_full_${SYSTEMATIC}.py

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
python $here/bin/run_one_analysis.py $configdir/config_${config}_${rn}_full_${SYSTEMATIC}.py

" \
| tee $here/logs/tmp/${rn}_${jobsuffix}_${SYSTEMATIC}${VERSION}.sh
chmod +x $here/logs/tmp/${rn}_${jobsuffix}_${SYSTEMATIC}${VERSION}.sh
bsub -G micegrp -M 20000 -oo $here/logs/${rn}_${jobsuffix}_${SYSTEMATIC}${VERSION}.log -q ${queue} $here/logs/tmp/${rn}_${jobsuffix}_${SYSTEMATIC}${VERSION}.sh

