#!/bin/bash

base_config="4"
new_config="4opt"

for emit in "3" "4" "6" "10" ; do
  for mom in "140" "170" "200" "240" ; do
    newtemplate=config_${new_config}_${emit}-${mom}.py
    cp config_${base_config}_${emit}-${mom}.py config_${new_config}_${emit}-${mom}.py 
    sed -i -e 's/"do_efficiency":True/"do_efficiency":False/g' -e 's/"do_extrapolation":True/"do_extrapolation":False/g' -e 's/"do_amplitude":True/"do_amplitude":False/g' -e 's/"do_density":True/"do_density":False/g' -e 's/"do_density_rogers":True/"do_density_rogers":False/g' -e 's/"do_plots":True/"do_plots":False/g' -e 's/"do_cuts_plots":True/"do_cuts_plots":False/g' -e 's/"do_optics":False/"do_optics":True/g' -e "s?output/c${base_config}?output/c${new_config}?g" $newtemplate


  done
done
