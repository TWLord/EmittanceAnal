#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

queue=xxl
#confignum=2
confignum=5
#queue=xlong
#queue=long


#opt_A=""
#opt_B=""
#opt_C=""
#opt_D=""
#opt_E=""
#opt_F=""
#opt_G=""

#3_140=""
#4_140=""
#6_140=""
#10_140=""
#3_170=""
#3_200=""
#3_240=""

for file in "$@" ; do
opt_A=""
opt_B=""
opt_C=""
opt_D=""
opt_E=""
opt_F=""
opt_G=""

while read -r line ; do
#echo $line
 rn=$(echo "${line}" |  cut -d'|' -f1 )
 ABS=$(echo "${line}" |  cut -d'|' -f7 )
 OpticsLong=$(echo "${line}" |  cut -d'|' -f4 )
 Optics=$(echo "${OpticsLong}" |  cut -d'+' -f1 )
 echo $rn
 echo $ABS
 #echo $OpticsLong
 #echo $Optics

case $Optics in

  "3-140")
  	#3_140+="$rn, "
  	opt_A="${opt_A}$rn, "
	;;

  "4-140")
  	#4_140+="$rn, "
  	opt_B="${opt_B}$rn, "
	;;

  "6-140")
  	#6_140+="$rn, "
  	opt_C="${opt_C}$rn, "
	;;

  "10-140")
  	#10_140+="$rn, "
  	opt_D="${opt_D}$rn, "
	;;

  "3-170")
  	#3_170+="$rn, "
  	opt_E="${opt_E}$rn, "
	;;

  "3-200")
  	#3_200+="$rn, "
  	opt_F="${opt_F}$rn, "
	;;

  "3-240")
  	#3_240+="$rn, "
  	opt_G="${opt_G}$rn, "
	;;

  *)
  	echo "No template for $Optics"
	;;
esac

done < $file
#done


if [ ! -z "$opt_A" ] ; then 
  opt_A=${opt_A/%??/}
  echo $opt_A
fi

if [ ! -z "$opt_B" ] ; then
  opt_B=${opt_B/%??/}
  echo $opt_B
fi

if [ ! -z "$opt_C" ] ; then
  opt_C=${opt_C/%??/}
  echo $opt_C
fi

if [ ! -z "$opt_D" ] ; then 
  opt_D=${opt_D/%??/}
  echo $opt_D
fi

if [ ! -z "$opt_E" ] ; then 
  opt_E=${opt_E/%??/}
  echo $opt_E
fi

if [ ! -z "$opt_F" ] ; then 
  opt_F=${opt_F/%??/}
  echo $opt_F
fi

if [ ! -z "$opt_G" ] ; then 
  opt_G=${opt_G/%??/}
  echo $opt_G
fi 


#if [ $rn -lt 10000 ] ; then
#runnumber=0$rn
#else 
#runnumber=$rn
#fi

#for key in "${keys[@]}"; do
#	echo $key
#	echo $(echo $key)
#done

for opt in "$opt_A,3-140" "$opt_B,4-140" "$opt_C,6-140" "$opt_D,10-140" "$opt_E,3-170" "$opt_F,3-200" "$opt_G,3-240"; do 

runs="${opt%,*}"
if [ ! -z "$runs" ] ; then 

optics="${opt##*,}"
echo $runs
echo $optics
_runs="${runs//, /_}"
echo $_runs
configdir=config/optics/$optics

#templatedir=config/solenoid/2017-02-6/$ABS
templatedir=config/solenoid/2017-02-6/ABS-TEMPLATE

if [ ! -e $here/$configdir/config_${confignum}_${_runs}_full.py  ] ; then

echo "Missing config ${confignum} file for runs $runs"
echo "Making config ${confignum} for run $runs from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${runs}/g" -e "s/ABS/$ABS/g" $here/$templatedir/config_${confignum}_${optics}.py > $here/$configdir/config_${confignum}_${_runs}_full.py

else 
echo "Running config ${confignum} for run $runs"
fi


echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_${confignum}_${_runs}_full.py

" \
| tee $here/logs/tmp/${queue}_${_runs}_c${confignum}.sh
chmod +x $here/logs/tmp/${queue}_${_runs}_c${confignum}.sh
bsub -G micegrp -M 6000 -oo $here/logs/${queue}_${_runs}_c${confignum}.log -q ${queue} $here/logs/tmp/${queue}_${_runs}_c${confignum}.sh

else
echo "no runs for $opt"
fi

done

done
