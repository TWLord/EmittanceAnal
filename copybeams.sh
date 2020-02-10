#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
#MAUSdir=~/MICE/maus--versions/MAUSv3.3.0
beamsdir=$here/output/beams
systematicsdir=~/MICE/analMC/systematics_mc/beams
#/10069/


for rn in "9883" "9885" "9886" "10243" "10245" "10246" "10314" "10317" "10318" "10319" "10508" "10504" "10509" ; do 

if [ $rn -lt 10000 ] ; then
#runnumber=0$rn
runnumber=$rn
else 
runnumber=$rn
fi

if [ ! -e $systematicsdir/$runnumber/tku_5.json  ] ; then

echo "Copying beam from $beamsdir/$runnumber/plots_${rn}... to systematics dir $systematicsdir"

mkdir -p $systematicsdir/$runnumber
cp -f $beamsdir/plots_${rn}_*/data_recorder/tku_5.json $systematicsdir/$runnumber/

else 
echo "Already have beam for $rn in $systematicsdir/$runnumber "
fi

done
