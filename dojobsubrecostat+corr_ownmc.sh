#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

#queue=medium
queue=long
#queue=xlong

#VERSION=2
#VERSION=10
#VERSION=11
VERSION=20

#configdir=config/runs/$runnumber
templatedir=config/solenoid/2017-02-6/ABS-TEMPLATE/

#ABS=ABS-LH2
ABS=ABS-LH2-EMPTY

#for opt in "9883,3-140" "9885,6-140" "9886,10-140" ; do 
#for opt in "9911,3-170" "9910,3-200" "9909,3-240" ; do 
for opt in "10268,3-170" "10267,3-200" "10265,3-240" ; do 

rn="${opt%,*}"
if [ ! -z "$rn" ] ; then 

Optics="${opt##*,}"
echo $rn
echo $Optics
#_runs="${runs//, /_}"
#echo $_runs

#Optics=3-140

configdir=config/runs/$rn

if [ $rn -lt 10000 ] ; then
runnumber=0$rn
else 
runnumber=$rn
fi


if [ ! -e $here/$configdir/config_6_${rn}_full.py  ] ; then

echo "Missing config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" -e "s/VERSION/$VERSION/g" $here/$templatedir/config_6_${Optics}.py > $here/$configdir/config_6_${rn}_full.py

else 
echo "Running config for run $rn"
fi
echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_6_${rn}_full.py

" \
| tee $here/logs/tmp/${queue}_${runnumber}_recostat+corr_ownmc.sh
chmod +x $here/logs/tmp/${queue}_${runnumber}_recostat+corr_ownmc.sh
bsub -G micegrp -M 6000 -oo $here/logs/${queue}_${runnumber}_recostat+corr_ownmc.log -q ${queue} $here/logs/tmp/${queue}_${runnumber}_recostat+corr_ownmc.sh

else
echo "no runs for $opt"
fi

done
