#!/bin/bash

#output/c11/v3/v107/plots_Simulated_2017-02-6_3-140_ABS-LH2/mc_plots/x_vs_y_at_mc_virtual_*large.png 

parentdir="./compare_virtual_station_plots"
mkdir $parentdir 
for abs in 'ABS-LH2' 'ABS-LH2-EMPTY' 'ABS-SOLID-EMPTY' 'ABS-SOLID-LiH' ; do
  for var in "x_vs_y" "px_vs_py" ; do
    plotdir="output/c11/v3/v107/plots_Simulated_2017-02-6_3-140_$abs/mc_plots"
    newdir=$parentdir/$abs/ 
    mkdir $newdir
    cp $plotdir/${var}_at_mc_virtual_*hist.png $newdir/
    cp $plotdir/${var}_at_mc_virtual_*hist.eps $newdir/
  done
done
