#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

queue=xlong
#queue=xxl
#queue=long

#c=5
c=8

#ABS=ABS-LH2
#ABS=ABS-LH2-EMPTY
#ABS=ABS-SOLID-EMPTY
ABS=ABS-SOLID-LiH
templatedir=config/solenoid/2017-02-6/ABS-TEMPLATE/

#for opt in "9883,3-140" "9885,6-140" "9886,10-140" ; do 
#for opt in "10243,3-140" "10245,6-140" "10246,10-140" ; do 
#for opt in "10314,3-140" "10317,4-140" "10318,6-140" "10319,10-140" ; do 
#for opt in "10314,3-140" "10318,6-140" "10319,10-140" ; do 
#for opt in "10579,3-140" "1080,4-140" "10581,6-140" "10582,10-140" ; do 
for opt in "10508,3-140" "10504,4-140" "10509,6-140" ; do 
#for opt in "10579,3-140" "10581,6-140" "10582,10-140" ; do 
#for opt in "9883,3-140" ; do 
#for opt in "9885,6-140" ; do 
#for opt in "9886,10-140" ; do 
#for opt in "10243,3-140" ; do 
#for opt in "10243,3-140" "10245,6-140" ; do 
#for opt in "10246,10-140" ; do 
#logs/10246_systematics_tku_basev105.log

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

configdir=config/runs/$rn

if [ ! -e $here/$configdir/config_${c}_${rn}_full.py  ] ; then

echo "Missing c${c} config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" $here/$templatedir/config_${c}_${Optics}.py > $here/$configdir/config_${c}_${rn}_full.py

else 
echo "Running old config for run $rn"
fi
echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_${c}_${rn}_full.py

" \
| tee $here/logs/tmp/${runnumber}_c${c}.sh
chmod +x $here/logs/tmp/${runnumber}_c${c}.sh
bsub -G micegrp -M 16000 -oo $here/logs/${runnumber}_c${c}.log -q ${queue} $here/logs/tmp/${runnumber}_c${c}.sh

else
echo "no runs for $opt"
fi

done
