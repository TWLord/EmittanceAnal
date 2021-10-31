#!/bin/bash
here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
myMAUS=~/MICE/maus--versions/MAUSv3.3.2


for cut in "50mm" "75mm" "100mm" ; do
    configdir=config/testingfiducial_3-170/$cut

    for config in "config_2_8646_8655_8656_8660_8666_8705_8706_8710_8711_8712_8713_8714_8715_8717_8718_8719_8720_8721_8722_8723_8724_8725_8726_8727_8728_8729_8730_8731_full.py" "config_2_9160_9162_full.py" "config_2_8764_8766_8767_full.py" "config_2_9717_full.py" ; do

        bsub -G micegrp -oo $here/logs/${config}_${cut}.txt  -q xxl -M 16000 "source $myMAUS/env.sh ; cd $here ; python bin/run_one_analysis.py $configdir/$config "

    done
done
