#!/bin/bash

here=/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts
MAUSdir=~/MICE/maus--versions/MAUSv3.3.0

queue=xxl
confignum=2
# CC is set from GeomID file. 
# CC template currently set as 2017-02-6

### Loop can be set to only submit higher mom runs

#confignum=5
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
echo $file
echo "$file"
GeomIDtmp="${file##*/}"
GeomID="${GeomIDtmp%_*}"
GeomID="${GeomID#sorted}"
echo GeomID
echo $GeomID
CCtmp="${file##*solenoid}"
CC="${CCtmp%.txt}"
echo CC
echo $CC
echo CC dir
CC=${CC//./pt}
echo $CC


opt_A=""
opt_B=""
opt_C=""
opt_D=""
opt_E=""
opt_F=""
opt_G=""
opt_H=""
opt_I=""
opt_J=""
opt_K=""
opt_L=""
opt_M=""
opt_N=""
opt_O=""
opt_P=""

while read -r line ; do
#echo $line
 rn=$(echo "${line}" |  cut -d'|' -f1 )
 ABS=$(echo "${line}" |  cut -d'|' -f7 )
 OpticsLong=$(echo "${line}" |  cut -d'|' -f4 )
 Optics=$(echo "${OpticsLong}" |  cut -d'+' -f1 )
 echo $rn
 echo $ABS
 if [ $ABS == "WEDGE" ] ; then
  echo "skipped $ABS run"
  continue;
 fi

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

  "4-170")
  	#3_170+="$rn, "
  	opt_H="${opt_H}$rn, "
	;;

  "4-200")
  	#3_200+="$rn, "
  	opt_I="${opt_I}$rn, "
	;;

  "4-240")
  	#3_240+="$rn, "
  	opt_J="${opt_J}$rn, "
	;;

  "6-170")
  	#3_170+="$rn, "
  	opt_K="${opt_K}$rn, "
	;;

  "6-200")
  	#3_200+="$rn, "
  	opt_L="${opt_L}$rn, "
	;;

  "6-240")
  	#3_240+="$rn, "
  	opt_M="${opt_M}$rn, "
	;;

  "10-170")
  	#3_170+="$rn, "
  	opt_N="${opt_N}$rn, "
	;;

  "10-200")
  	#3_200+="$rn, "
  	opt_O="${opt_O}$rn, "
	;;

  "10-240")
  	#3_240+="$rn, "
  	opt_P="${opt_P}$rn, "
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

if [ ! -z "$opt_H" ] ; then 
  opt_H=${opt_H/%??/}
  echo $opt_H
fi 

if [ ! -z "$opt_I" ] ; then 
  opt_I=${opt_I/%??/}
  echo $opt_I
fi 

if [ ! -z "$opt_J" ] ; then 
  opt_J=${opt_J/%??/}
  echo $opt_J
fi 

if [ ! -z "$opt_K" ] ; then 
  opt_K=${opt_K/%??/}
  echo $opt_K
fi 

if [ ! -z "$opt_L" ] ; then 
  opt_L=${opt_L/%??/}
  echo $opt_L
fi 

if [ ! -z "$opt_M" ] ; then 
  opt_M=${opt_M/%??/}
  echo $opt_M
fi 

if [ ! -z "$opt_N" ] ; then 
  opt_N=${opt_N/%??/}
  echo $opt_N
fi 

if [ ! -z "$opt_O" ] ; then 
  opt_O=${opt_O/%??/}
  echo $opt_O
fi 

if [ ! -z "$opt_P" ] ; then 
  opt_P=${opt_P/%??/}
  echo $opt_P
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

#for opt in "$opt_A,3-140" "$opt_B,4-140" "$opt_C,6-140" "$opt_D,10-140" "$opt_E,3-170" "$opt_F,3-200" "$opt_G,3-240" "$opt_H,4-170" "$opt_I,4-200" "$opt_J,4-240" "$opt_K,6-170" "$opt_L,6-200" "$opt_M,6-240" "$opt_N,10-170" "$opt_O,10-200" "$opt_P,10-240"; do 
for opt in "$opt_E,3-170" "$opt_F,3-200" "$opt_G,3-240" "$opt_H,4-170" "$opt_I,4-200" "$opt_J,4-240" "$opt_K,6-170" "$opt_L,6-200" "$opt_M,6-240" "$opt_N,10-170" "$opt_O,10-200" "$opt_P,10-240"; do 

runs="${opt%,*}"
if [ ! -z "$runs" ] ; then 

optics="${opt##*,}"
echo $runs
echo $optics
_runs="${runs//, /_}"
echo $_runs

#CC="2017-02-6"
configdir=config/$CC/$optics
mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/config/
cp -f $here/$templatedir/__init__.py $here/config/$CC/
cp -f $here/$templatedir/__init__.py $here/config/$CC/$optics/

#configdir=config/optics/$optics

#templatedir=config/solenoid/2017-02-6/$ABS
templatedir=config/solenoid/2017-02-6/ABS-TEMPLATE
#templatedir=config/solenoid/${CC}/ABS-TEMPLATE

if [ ! -e $here/$configdir/config_${confignum}_GeomID${GeomID}_${_runs}_full.py  ] ; then

echo "Missing config ${confignum} file for runs $runs"
echo "Making config ${confignum} for run $runs from template"

mkdir -p $here/$configdir
cp -f $here/$templatedir/__init__.py $here/$configdir/

sed -e "s/template/${runs}/g" -e "s/ABS/$ABS/g" -e "s?reconOnly?reconOnly/Geom${GeomID}?g" -e "s/2017-02-6/${CC}/g" $here/$templatedir/config_${confignum}_${optics}.py > $here/$configdir/config_${confignum}_GeomID${GeomID}_${_runs}_full.py

else 
echo "Running config ${confignum} for run $runs"
fi


echo -en "#!/bin/bash \n\

. $MAUSdir/env.sh 
cd $MAUSdir/bin/user/first-observation-paper-scripts 


python bin/run_one_analysis.py $configdir/config_${confignum}_GeomID${GeomID}_${_runs}_full.py

" \
| tee $here/logs/tmp/${queue}_${_runs}_GeomID${GeomID}_c${confignum}.sh
chmod +x $here/logs/tmp/${queue}_${_runs}_GeomID${GeomID}_c${confignum}.sh
bsub -G micegrp -M 6000 -oo $here/logs/${queue}_${_runs}_GeomID${GeomID}_c${confignum}.log -q ${queue} $here/logs/tmp/${queue}_${_runs}_GeomID${GeomID}_c${confignum}.sh

#else
#echo "no runs for $opt"
fi

done

done
