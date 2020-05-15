#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

ABS="$1"
rn="$2"
Optics="$3"
CC="$4"
VERSION="$5"
config="$6"
queue="$7"
templatedir="$8"
jobsuffix="$9"
#datadir="$10"

echo $rn
echo $Optics

if [ $rn -lt 10000 ] ; then
runnumber=0$rn
else 
runnumber=$rn
fi
rn=$rn

if [ $config == "2f" ] ; then
datadir=/data/mice/phumhf/ReconData/Mausv3.3.2/$runnumber
elif [ $config == "3f" ] ; then
datadir=/data/mice/phumhf/MC/MAUSv3.3.2/$runnumber$VERSION
else
echo "XXXXXX --- WRONG SCRIPT FOR CONFIG --- XXXXXX"
exit 1
fi




configdir=config/$config

if [ ! -d $here/config/$config ] ; then

echo "Making new parent directory $here/config/$config/ "
mkdir -p $here/config/$config
cp -f $here/$templatedir/__init__.py $here/config/$config/
fi

if [ ! -e $here/$configdir/config_${config}_${rn}_full.py  ] ; then

echo "Missing $config config file for run $rn"
echo "Making $config config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" -e "s/CC/$CC/g" -e "s/VERSION/$VERSION/g" -e "s%.*a_file = .*%        a_file = \"$datadir/*.root\"%"  $here/$templatedir/config_${config}_${Optics}.py > $here/$configdir/config_${config}_${rn}_full.py

else 
echo "Running $config config for run $rn"
fi
echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $here

PYTHONPATH=\$PYTHONPATH:$here
echo \$PYTHONPATH
python $here/bin/run_file_reducer.py $configdir/config_${config}_${rn}_full.py

" \
| tee $here/logs/tmp/${runnumber}_${jobsuffix}.sh
chmod +x $here/logs/tmp/${runnumber}_${jobsuffix}.sh
#bsub -G micegrp -M 2000 -oo $here/logs/${runnumber}_${jobsuffix}.log -q ${queue} $here/logs/tmp/${runnumber}_${jobsuffix}.sh
bsub -G micegrp -M 20000 -oo $here/logs/${runnumber}_${jobsuffix}.log -q ${queue} $here/logs/tmp/${runnumber}_${jobsuffix}.sh

