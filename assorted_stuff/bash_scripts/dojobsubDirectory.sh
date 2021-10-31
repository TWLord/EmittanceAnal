#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

queue=xlong
#queue=xlong
#queue=long

for inp in "$@" ; do
if [ "${inp: -1}" == "/" ] ; then
inp=${inp%?}
fi
echo "Directory is $inp"

if [ -d $inp ] ; then
DIR=$inp
else
echo "File name given, not dir."
echo "Exiting.."
exit 1
fi

if [ ! -e $DIR/__init__.py ] ; then
cp $here/config/__init__.py $DIR
fi

for file in "$DIR"/* ; do

if [[ ! $file =~ "__init__.py" ]] ; then
echo $file

file="${file##*/}"
echo "Running $file "


echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $DIR/$file

" \
| tee $here/logs/tmp/${queue}_${file}.sh
chmod +x $here/logs/tmp/${queue}_${file}.sh
bsub -G micegrp -M 20000 -oo $here/logs/${queue}_${file}.log -q ${queue} $here/logs/tmp/${queue}_${file}.sh

fi

done
done
