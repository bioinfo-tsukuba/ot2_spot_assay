#!/bin/bash
set eu
cd ~
ymdhms=$(date "+%Y-%m%d-%H%M%S")
ymdhmsforcalc=$(date "+%s")
target_dir=$HOME/Documents/scan_90min/${ymdhms}_spotassay
mkdir -p $target_dir
cd $target_dir
count=1
while :
do
 echo "$count times"
 tmptime=$(date "+%s")
 #expr \($tmptime - $ymdhmsforcalc\) / 60
 min=$(echo $(((tmptime-ymdhmsforcalc)/60)))
 scanimage --device "epson2:libusb:001:008" --mode Color --resolution 600 --format=tiff > scan_${count}_${min}min.tiff &
 count=$((count+1))
 sleep 90m
done