#!/bin/bash

base_config="2"
new_config="beams"

for emit in "3" "4" "6" "10" ; do
  for mom in "140" "170" "200" "240" ; do
    newtemplate=config_${new_config}_${emit}-${mom}.py
    cp config_${base_config}_${emit}-${mom}.py config_${new_config}_${emit}-${mom}.py 
    sed -i -e 's/"do_amplitude":True/"do_amplitude":False/g' -e 's/"do_data_recorder":False/"do_data_recorder":True/g' -e "s?output/c${base_config}?output/beams?g" $newtemplate

  done
done


