#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

queue=xlong
#queue=long

for file in "$@" ; do
while read -r line ; do
#echo $line
 rn=$(echo "${line}" |  cut -d'|' -f1 )
 ABS=$(echo "${line}" |  cut -d'|' -f7 )
 OpticsLong=$(echo "${line}" |  cut -d'|' -f4 )
 Optics=$(echo "${OpticsLong}" |  cut -d'+' -f1 )
 echo $rn
 echo $ABS
 echo $OpticsLong
 echo $Optics

#if [ "$Optics" = "3-170" ] || [ "$Optics" = "3-200" ] || [ "$Optics" = "3-240" ] 

if [ $rn -lt 10000 ] ; then
runnumber=0$rn
else 
runnumber=$rn
fi


configdir=config/runs/$rn
#templatedir=config/solenoid/2017-02-6/$ABS
templatedir=config/solenoid/2017-02-6/ABS-TEMPLATE/

if [ ! -e $here/$configdir/config_2_${rn}_full.py  ] ; then

if [ "$Optics" != "3-140" ] && [ "$Optics" != "4-140" ] && [ "$Optics" != "6-140" ] && [ "$Optics" != "10-140" ] && [ "$Optics" != "3-170" ] && [ "$Optics" != "3-200" ] && [ "$Optics" != "3-240" ]; then 
  echo "Optics = $Optics, no template available"
  echo " -- Skipping -- "
  continue
fi


echo "Missing config file for run $rn"
echo "Making config for run $rn from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${rn}/g" -e "s/ABS/$ABS/g" $here/$templatedir/config_2_${Optics}.py > $here/$configdir/config_2_${rn}_full.py

else 
echo "Running config for run $rn"
fi


echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_2_${rn}_full.py

" \
| tee $here/logs/tmp/${queue}_${rn}_reco.sh
chmod +x $here/logs/tmp/${queue}_${rn}_reco.sh
bsub -G micegrp -M 6000 -oo $here/logs/${queue}_${rn}_reco.log -q ${queue} $here/logs/tmp/${queue}_${rn}_reco.sh
#bsub -G micegrp -M 6000 -eo $here/logs/${queue}_${rn}_reco.error -oo $here/logs/${queue}_${rn}_reco.log -q ${queue} $here/logs/tmp/${queue}_${rn}_reco.sh





done < $file
done

