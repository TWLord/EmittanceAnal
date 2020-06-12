#!/bin/bash

base_config="9"
new_config="11"

for emit in "3" "4" "6" "10" ; do
  for mom in "140" "170" "200" "240" ; do

    cp config_${base_config}_${emit}-${mom}.py config_${new_config}_${emit}-${mom}.py 

  done
done
