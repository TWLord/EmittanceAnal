#!/bin/bash

#olddir="/data/mice/phumhf/backupOutput/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c10/plots_Simulated_2017-02-6_10-140_ABS-LH2/mc_plots/"
#newdir="residualplots/Simulated_2017-02-6_10-140_ABS-LH2"
olddir="/data/mice/phumhf/backupOutput/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c10/plots_Simulated_2017-02-6_3-140_ABS-SOLID-EMPTY/mc_plots/"
newdir="residualplots/Simulated_2017-02-6_3-140_ABS-SOLID-EMPTY"
mkdir -p ./$newdir
for tracker in "tku" "tkd" ; do
  for ptype in "compare" "residual" ; do
    for img in "png" "eps" ; do
      for plot in mc_${ptype}_${tracker}_tp_pz.${img} mc_${ptype}_${tracker}_tp_x.${img} mc_${ptype}_${tracker}_tp_p.${img}  mc_${ptype}_${tracker}_tp_y.${img} mc_${ptype}_${tracker}_tp_pt.${img}  mc_${ptype}_${tracker}_tp_z.${img}  mc_${ptype}_${tracker}_tp_px.${img}  mc_${ptype}_${tracker}_tp_py.${img}  ; do

        cp -f ${olddir}/$plot ./$newdir

      done
    done
  done
done



