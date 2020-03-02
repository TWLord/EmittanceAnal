#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

#queue=medium
#queue=long
#queue=xlong
queue=xxl

#VERSION=6
#VERSION=2
#VERSION=3
#VERSION=4
#VERSION=5
#VERSION=6
#VERSION=7
#VERSION=8
#VERSION=9
#VERSION=10
#VERSION=11

#VERSION=20
#VERSION=21
#VERSION=22
#VERSION=23
#VERSION=24
#VERSION=25
#VERSION=26
VERSION=27

#VERSION="test"

#VERSION=125

#sleep 4h

templatedir=config/solenoid/2017-02-6/ABS-TEMPLATE/

ABS=ABS-LH2
#ABS=ABS-LH2-EMPTY
#ABS=ABS-SOLID-LiH
#ABS=ABS-SOLID-EMPTY

#for opt in "9883,3-140" "9885,6-140" "9886,10-140" ; do 
#for opt in "10243,3-140" "10245,6-140" "10246,10-140" ; do 
#for opt in "10323,3-140" "10324,6-140" "10325,10-140" ; do 
#for opt in "10579,3-140" "10581,6-140" "10582,10-140" ; do 
#for opt in "10508,3-140" ; do 
#for opt in "9883,3-140" ; do 
#for opt in "9885,6-140" ; do 
#for opt in "9886,10-140" ; do 
#for opt in "10243,3-140" ; do 

#for opt in "9911,3-170" "9910,3-200" "9909,3-240" ; do 
for opt in "9909,3-240" ; do 
#for opt in "9911,3-170" "9910,3-200" ; do 
#for opt in "9910,3-200" "9909,3-240" ; do 
#for opt in "9911,3-170" ; do 

#for opt in "10268,3-170" "10267,3-200" "10265,3-240" ; do 
#for opt in "10268,3-170" ; do 
#for opt in "10267,3-200" "10265,3-240" ; do 
#for opt in "10267,3-200" ; do 

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
configdir=config/ownmc/v$VERSION

if [ ! -e $here/$configdir/config_4_${rn}_full.py  ] ; then

echo "Missing config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" -e "s/VERSION/$VERSION/g" $here/$templatedir/config_4_${Optics}.py > $here/$configdir/config_4_${rn}_full.py

else 
echo "Running config for run $rn"
fi
echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_4_${rn}_full.py

" \
| tee $here/logs/tmp/${runnumber}_ownmcv${VERSION}.sh
chmod +x $here/logs/tmp/${runnumber}_ownmcv${VERSION}.sh
bsub -G micegrp -M 16000 -oo $here/logs/${runnumber}_ownmcv${VERSION}.log -q ${queue} $here/logs/tmp/${runnumber}_ownmcv${VERSION}.sh
#bsub -G micegrp -M 6000 -oo $here/logs/${runnumber}_ownmcv${VERSION}.log -q ${queue} $here/logs/tmp/${runnumber}_ownmcv${VERSION}.sh

else
echo "no runs for $opt"
fi

done
