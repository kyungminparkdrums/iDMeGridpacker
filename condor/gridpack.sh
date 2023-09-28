#!/bin/bash

set -x

m1=$1
delta=$2
onejet=$3
mA_over_m1=$4

mkdir gridpacks
cd gridpacks

tar xf ../submit.tar.gz

cd bin/MadGraph5_aMCatNLO/iDMeGridpacker/

python makeGridpack_electrons.py --m1 $m1 --delta $delta --onejet $onejet --mA_over_m1 $mA_over_m1

cd ..
ls

outfile=$(ls | grep ".tar.xz")

echo outfile

xrdcp $outfile root://cmseos.fnal.gov//store/group/lpcmetx/iDMe/gridpacks/
