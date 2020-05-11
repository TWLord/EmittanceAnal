#!/bin/bash

newrn="10508"
newsys="tku_rot_plus"
vers="v106"

for i in `seq 0 0` ; do
echo $i
newfile="config_7_${newrn}${vers}_${newsys}${i}.py"
cp config_7_10509_tku_density_plus.py $newfile 

#set i to 4 digits e.g. 0001
#change file dirs to only i with sed 

sed -i -e "s/10509/${newrn}/g" -e "s#tku_density_plus#${newsys}#g" -e "s#output/systematics/2017-02-6-c7_v105#output/systematics/${i}#g" -e "s#v105#${vers}#g" $newfile  


done
