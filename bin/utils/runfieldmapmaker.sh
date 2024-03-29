#!/bin/bash

cd /home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
. ../../../env.sh
cd bin/utils

#for rn in 9883 9885 9886 10243 10245 10246 10313 10315 10318 10319 10508 10504 10509 ; do 
for rn in 9909 9910 9911 10265 10267 10268 ; do 

if [ $rn -lt 10000 ] ; then
 runnumber=0$rn
else
 runnumber=$rn
fi

mkdir -p ./fields_$rn

python make_field_map.py --simulation_geometry_filename /data/mice/phumhf/Geometries/runnumber_$runnumber/ParentGeometryFile.dat
#python make_field_map.py --simulation_geometry_filename /data/mice/phumhf/ReconData/Mausv3.3.2/$runnumber/geo-$runnumber/ParentGeometryFile.dat


mv field/ fields_$rn/

done
