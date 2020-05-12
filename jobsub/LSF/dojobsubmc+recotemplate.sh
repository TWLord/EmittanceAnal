#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

#queue=xlong
#queue=xxl
queue=long

#ABS=ABS-LH2
#ABS=ABS-LH2-EMPTY
ABS=SOLID-EMPTY
#ABS=SOLID-LiH
templatedir=config/solenoid/2017-02-6/ABS-TEMPLATE/

#for opt in "9883,3-140" "9885,6-140" "9886,10-140" ; do 
#for opt in "10243,3-140" "10245,6-140" "10246,10-140" ; do 
#for opt in "10314,3-140" "10317,4-140" "10318,6-140" "10319,10-140" ; do 
for opt in "10314,3-140" "10318,6-140" "10319,10-140" ; do 
#for opt in "10579,3-140" "10580,4-140" "10581,6-140" "10582,10-140" ; do 
#for opt in "10579,3-140" "10581,6-140" "10582,10-140" ; do 
#for opt in "9883,3-140" ; do 
#for opt in "9885,6-140" ; do 
#for opt in "9886,10-140" ; do 
#for opt in "10246,10-140" ; do 
#for opt in "10319,10-140" ; do 
#for opt in "10243,3-140" ; do 

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

if [ ! -e $here/$configdir/config_3_${rn}_full.py  ] ; then

echo "Missing config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" -e "s/VERSION/$VERSION/g" $here/$templatedir/config_3_${Optics}.py > $here/$configdir/config_3_${rn}_full.py

else 
echo "Running config 3 for run $rn"
fi

if [ ! -e $here/$configdir/config_5_${rn}_full.py  ] ; then

echo "Missing config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" $here/$templatedir/config_5_${Optics}.py > $here/$configdir/config_5_${rn}_full.py

else 
echo "Running config 5 for run $rn"
fi

echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_3_${rn}_full.py
python bin/run_one_analysis.py $configdir/config_5_${rn}_full.py

" \
| tee $here/logs/tmp/${runnumber}_mc+reco.sh
chmod +x $here/logs/tmp/${runnumber}_mc+reco.sh
bsub -G micegrp -M 20000 -oo $here/logs/${runnumber}_mc+reco.log -q ${queue} $here/logs/tmp/${runnumber}_mc+reco.sh
#bsub -G micegrp -M 16000 -eo $here/logs/${runnumber}_mc.error -oo $here/logs/${runnumber}_mc.log -q ${queue} $here/logs/tmp/${runnumber}_mc.sh

else
echo "no runs for $opt"
fi

done
