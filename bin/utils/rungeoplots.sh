#!/bin/bash

MAUSdir=/storage/epp2/phumhf/MICE/maus--versions/MAUSv3.3.2
GEOMdir=/storage/epp2/phumhf/MICE/Geometries
here=$PWD
base=$PWD/../../
echo "here $here"
echo "base $base"

. $MAUSdir/env.sh

#for rn in 9883 9885 9886 10243 10245 10246 10313 10315 10318 10319 10508 10504 10509 ; do 
#for rn in 9883 9886 10243 10245 10246 10313 10315 10318 10319 10508 10504 10509 ; do 
for rn in 9883 10243 10314 10508 ; do 
#for rn in 9909 9910 9911 10268 10267 10265 ; do 
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

##ln -s /data/mice/phumhf/ReconData/Mausv3.3.2/$runnumber/geo-$runnumber/ geomplots_$rn/
#ln -s /data/mice/phumhf/ReconData/Mausv3.3.2/$runnumber/geo-$runnumber/ ./
ln -s $GEOMdir/runnumber_$runnumber/ ./


#python check_geometry.py --simulation_geometry_filename /data/mice/phumhf/Geometries/runnumber_09885/ParentGeometryFile.dat 

#python $here/check_geometry.py --simulation_geometry_filename geo-$runnumber/ParentGeometryFile.dat 
python $here/check_geometry.py --simulation_geometry_filename runnumber_$runnumber/ParentGeometryFile.dat 

mv plots geomplots_$rn/ 

done
