#!/bin/bash

for run in 9883 9885 ; do
for sys in "tku_base" "tku_pos_plus" "tku_rot_plus" "tku_scale_C_plus" "tku_scale_E1_plus" "tku_scale_E2_plus" "tku_density_plus" "tkd_rot_plus" "tkd_pos_plus" "tkd_scale_C_plus" "tkd_scale_E1_plus" "tkd_scale_E2_plus" "tkd_density_plus" ;  do

echo $sys : 
ls -rt /data/mice/phumhf/analMC/${run}_systematics_v107/$sys/*/maus_reconstruction.root | wc -l

done
done
