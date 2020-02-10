#!/bin/bash

cd /home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
base=$PWD
. ../../../env.sh
cd bin/utils
here=$PWD

#for rn in 9883 9885 9886 10243 10245 10246 10313 10315 10318 10319 10508 10504 10509 ; do 
for rn in 9883 9886 10243 10245 10246 10313 10315 10318 10319 10508 10504 10509 ; do 
#for rn in 9886 ; do 
#for rn in 9885 ; do 

cd $here 

if [ $rn -lt 10000 ] ; then
 runnumber=0$rn
else
 runnumber=$rn
fi

#cd $base
mkdir -p ./geomplots_$rn
cd geomplots_$rn
mkdir -p ./plots

#ln -s /data/mice/phumhf/ReconData/Mausv3.3.2/$runnumber/geo-$runnumber/ geomplots_$rn/
ln -s /data/mice/phumhf/ReconData/Mausv3.3.2/$runnumber/geo-$runnumber/ ./


#python check_geometry.py --simulation_geometry_filename /data/mice/phumhf/Geometries/runnumber_09885/ParentGeometryFile.dat 
python $here/check_geometry.py --simulation_geometry_filename geo-$runnumber/ParentGeometryFile.dat 

mv plots geomplots_$rn/ 

done
