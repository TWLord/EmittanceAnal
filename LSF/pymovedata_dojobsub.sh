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
GEOPATH="${11}"
use_preanal="${12}"
SYSTEMATIC="${13}"
SYSVERS="${14}"
#datadir="$11"

if [ -z $SYSVERS ] ; then
SYSVERS="no_sys"
fi

echo $rn
echo $Optics

#if [ $rn -lt 10000 ] ; then
#runnumber=0$rn
#else 
#runnumber=$rn
#fi
#rn=$rn

if [ $config == "1" ] ; then
datadir=/data/mice/phumhf/MC/MAUSv3.3.2/$runnumber$VERSION
elif [ $config == "2" ] ; then
datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "2opt" ] ; then
datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "3" ] ; then
datadir=/data/mice/phumhf/MC/MAUSv3.3.2/$runnumber$VERSION
elif [ $config == "3opt" ] ; then
datadir=/data/mice/phumhf/MC/MAUSv3.3.2/$runnumber$VERSION
elif [ $config == "4" ] ; then
datadir=/data/mice/phumhf/analMC/${runnumber}_$VERSION
copydir=*/maus_output
elif [ $config == "4opt" ] ; then
datadir=/data/mice/phumhf/analMC/${runnumber}_$VERSION
copydir=*/maus_output
elif [ $config == "4ang" ] ; then
datadir=/data/mice/phumhf/analMC/${runnumber}_$VERSION
copydir=*/maus_output
elif [ $config == "5" ] ; then
datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "6" ] ; then
datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "7" ] ; then
echo "[ERROR]: Shouldn't be running systematics from this script. Exiting.."
exit 1
elif [ $config == "8" ] ; then
datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "9" ] ; then
datadir=/data/mice/phumhf/MC/MAUSv3.3.2/$runnumber$VERSION
elif [ $config == "10" ] ; then
datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "11" ] ; then
datadir=/data/mice/phumhf/MC/MAUSv3.3.2/$runnumber$VERSION
elif [ $config == "12" ] ; then
datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "13" ] ; then
datadir=/data/mice/phumhf/MC/MAUSv3.3.2/$runnumber$VERSION
elif [ $config == "14" ] ; then
datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "15" ] ; then
datadir=/data/mice/phumhf/MC/MAUSv3.3.2/$runnumber$VERSION
elif [ $config == "16" ] ; then
datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "17" ] ; then
datadir=/data/mice/phumhf/MC/MAUSv3.3.2/$runnumber$VERSION
elif [ $config == "18" ] ; then
datadir=/data/mice/phumhf/ReconData/MAUSv3.3.2/$runnumber
elif [ $config == "19" ] ; then
datadir=/data/mice/phumhf/MC/MAUSv3.3.2/$runnumber$VERSION
else 
echo "NO CONFIG SET UP FOR $config in pymovedata_jobsub script ---- EXITING"
fi


configdir=config/c$config/movedata/$VERSION/$SYSVERS

if [ ! -d $here/$configdir ] ; then

echo "Making new parent directory $here/config/c$config/ "
mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/config/c$config/
cp -f $here/$templatedir/__init__.py $here/config/c$config/movedata/
cp -f $here/$templatedir/__init__.py $here/config/c$config/movedata/$VERSION/
cp -f $here/$templatedir/__init__.py $here/config/c$config/movedata/$VERSION/$SYSVERS/
fi

if [ ! -e $here/$configdir/config_${config}_${rn}_full.py  ] ; then

echo "Missing config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" -e "s/CC/$CC/g" -e "s/VERSION/$VERSION/g" -e "s/SYSTEMATIC/$SYSTEMATIC/g" -e "s/SYSVERS/$SYSVERS/g" -e "s?GEOPATH?$GEOPATH?g" $here/$templatedir/config_${config}_${Optics}.py > $here/$configdir/config_${config}_${rn}_full.py

#sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" -e "s/CC/$CC/g" -e "s/VERSION/$VERSION/g" $here/$templatedir/config_${config}_${Optics}.py > $here/$configdir/config_${config}_${rn}_full.py


else 
echo "Running config for run $rn"
fi

if [ $use_preanal == "True" ] ; then
echo "Using preanal dicts"
sed -i "s?reduced_dict_path = .*?reduced_dict_path = \"reduced_files/MC$VERSION/${rn}/\"?" $here/$configdir/config_${config}_${rn}_full.py 

#sed -i "254s?.*?    reduced_dict_path = \"reduced_files/MC$VERSION/${rn}/\"?" $here/$configdir/config_${config}_${rn}_full.py 
else
echo "Not using preanal dicts"
sed -i "s?reduced_dict_path = .*?reduced_dict_path = None?" $here/$configdir/config_${config}_${rn}_full.py 
#sed -i "254s?.*? ?" $here/$configdir/config_${config}_${rn}_full.py 
fi

echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 

mytempdir=\"\$(mktemp -d)\"
cd \$mytempdir
echo \"Making temp dir \$mytempdir \"

echo \" ---- Copying root files for analysis ---- \"
cd $datadir
echo cp --parents ./${copydir}*.root \$mytempdir/
cp --parents ./${copydir}*.root \$mytempdir/

#echo cp $datadir/*.root \$mytempdir/
#cp $datadir/*.root \$mytempdir/

sed -i \"s%.*a_file = .*%        a_file = \\\"\$mytempdir\/\\${copydir}*.root\\\"%\" $here/$configdir/config_${config}_${rn}_full.py

echo \"Copied files : \"
echo \"\$(ls)\"

cd $here

PYTHONPATH=\$PYTHONPATH:$here
echo \$PYTHONPATH
python $here/bin/run_one_analysis.py $configdir/config_${config}_${rn}_full.py

" \
| tee $here/logs/tmp/${runnumber}_${jobsuffix}_${VERSION}_${SYSVERS}_movedata.sh
chmod +x $here/logs/tmp/${runnumber}_${jobsuffix}_${VERSION}_${SYSVERS}_movedata.sh
#bsub -G micegrp -M 20000 -oo $here/logs/${runnumber}_${jobsuffix}_${VERSION}_${SYSVERS}_movedata.log -q ${queue} $here/logs/tmp/${runnumber}_${jobsuffix}_${VERSION}_${SYSVERS}_movedata.sh
bsub -G micegrp -M 24000 -oo $here/logs/${runnumber}_${jobsuffix}_${VERSION}_${SYSVERS}_movedata.log -q ${queue} $here/logs/tmp/${runnumber}_${jobsuffix}_${VERSION}_${SYSVERS}_movedata.sh

