#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

#queue=medium
queue=long
#queue=xlong

VERSION=105

templatedir=config/solenoid/2017-02-6/ABS-TEMPLATE/
#ABS=ABS-LH2-EMPTY
#ABS=ABS-SOLID-EMPTY

set -- "ABS-LH2" "9883,3-140" "ABS-LH2" "9885,6-140" "ABS-LH2" "9886,10-140" "ABS-LH2-EMPTY" "10243,3-140" "ABS-LH2-EMPTY" "10245,6-140" "ABS-LH2-EMPTY" "10246,10-140" "ABS-SOLID-EMPTY" "10314,3-140" "ABS-SOLID-EMPTY" "10317,4-140" "ABS-SOLID-EMPTY" "10318,6-140" "ABS-SOLID-EMPTY" "10319,10-140" "ABS-SOLID-LiH" "10508,3-140" "ABS-SOLID-LiH" "10504,4-140" "ABS-SOLID-LiH" "10509,6-140"
#set -- "ABS-LH2" "9883,3-140" "ABS-SOLID-LiH" "10509,6-140"

while [ "$#" -gt 0 ]; do

ABS=$1
opt=$2
shift 2

for systematic in "tku_base" ; do
#for systematic in "tku_base" "tku_pos_plus" "tku_scale_E1_plus" "tku_density_plus" "tkd_pos_plus" "tkd_scale_E1_plus" "tkd_density_plus" "tku_rot_plus" "tku_scale_C_plus" "tku_scale_E2_plus" "tkd_rot_plus" "tkd_scale_C_plus" "tkd_scale_E2_plus" ; do

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

#configdir=config/runs/$runnumber
configdir=config/systematics/v$VERSION

if [ ! -e $here/$configdir/config_7_${rn}_${systematic}.py  ] ; then

echo "Missing config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" -e "s/SYSTEMATIC/$systematic/g" -e "s/VERSION/$VERSION/g" $here/$templatedir/config_7_${Optics}.py > $here/$configdir/config_7_${rn}_${systematic}.py

else 
echo "Running config for run $rn"
fi
echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_7_${rn}_${systematic}.py

" \
| tee $here/logs/tmp/${runnumber}_systematics_${systematic}v${VERSION}.sh
chmod +x $here/logs/tmp/${runnumber}_systematics_${systematic}v${VERSION}.sh
bsub -G micegrp -M 16000 -oo $here/logs/${runnumber}_systematics_${systematic}v${VERSION}.log -q ${queue} $here/logs/tmp/${runnumber}_systematics_${systematic}v${VERSION}.sh

else
echo "no runs for $opt"
fi

done

done



#ABS=ABS-LH2
#ABS=ABS-LH2-EMPTY
#ABS=ABS-SOLID-EMPTY
#ABS=ABS-SOLID-LiH

#for opt in "9883,3-140" ; do 
#for opt in "9886,10-140" ; do 
#for opt in "9883,3-140" "9885,6-140" "9886,10-140" ; do 
#for opt in "10243,3-140" "10245,6-140" "10246,10-140" ; do 
#for opt in "10314,3-140" "10317,4-140" "10318,6-140" "10319,10-140" ; do 
#for opt in "10508,3-140" "10504,4-140" "10509,6-140" ; do 

#for opt in "9911,3-170" "9910,3-200" "9909,3-240" ; do 
#for opt in "10268,3-170" "10267,3-200" "10265,3-240" ; do 
