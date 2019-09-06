#!/bin/bash

cd /home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
. ../../../env.sh
cd bin/utils

python check_geometry.py --simulation_geometry_filename /data/mice/phumhf/Geometries/runnumber_09885/ParentGeometryFile.dat 
