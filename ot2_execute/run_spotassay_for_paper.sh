#!/usr/bin/env bash

# setting venv
conda deactivate
conda activate labopt
set -eu

# setting directory for each experiment
ymdhms=$(date "+%Y-%m%d-%H%M%S")
target_dir=$HOME/Documents/protocols_spotassay/${ymdhms}_spotassay
cd ~
mkdir -p $HOME/Documents/protocols_spotassay/${ymdhms}_spotassay
cd $target_dir


######################### setting variables #########################
## maiking config.csv file in the current dir
touch config.csv
echo "key,value,description" >> config.csv
echo "num_spot, ,The number of spot samples (1~7)" >> config.csv
echo "num_plate, ,The number of plates (1~4)" >> config.csv
echo "p300_start, ,p300 tip starting location (example B1)" >> config.csv
echo "p20_start, ,p20 tip starting location (example A2)" >> config.csv
echo "weight_plate1, ,Weight [g] of plate1 (on deck5) (with Petri dish lid)" >> config.csv
echo "weight_plate2, ,Weight [g] of plate2 (on deck6) (with Petri dish lid)" >> config.csv
echo "weight_plate3, ,Weight [g] of plate3 (on deck8) (with Petri dish lid)" >> config.csv
echo "weight_plate4, ,Weight [g] of plate4 (on deck9) (with Petri dish lid)" >> config.csv
echo -e "\n" >> config.csv
echo "NOTES: if you test less than two plates, fill in the blank with 0" >> config.csv
echo -e "\n" >> config.csv
echo "Save (commmand + S) and close" >> config.csv
open config.csv

## confirmation
read -p "Do you want to proceed with this configration? (yes/no) " yn
cat config.csv
echo -e "\n"
case $yn in 
	yes ) echo ok, we will proceed;;
	no ) echo exiting...;
		exit;;
	* ) echo invalid response;
esac

## storage variables
declare -a var=()
i=0
while [ $i -lt 10 ] && read line
do
var_temp=`echo ${line} | cut -d ',' -f 2`
var[i]=$var_temp
i=`expr $i + 1`
done < config.csv

read num_spot <<< ${var[1]}
read num_plate <<< ${var[2]}
read p300_start_raw <<< ${var[3]}
read p20_start_raw <<< ${var[4]}
read weight_plate1 <<< ${var[5]}
read weight_plate2 <<< ${var[6]}
read weight_plate3 <<< ${var[7]}
read weight_plate4 <<< ${var[8]}

## starting tip calculation
alphabet300=$(printf ${p300_start_raw:0:1})
ASCIIcode300=$(printf "%02d" \"${alphabet300})
p300_start=$((${ASCIIcode300} - 65 - 8 + ${p300_start_raw:1}*8))

alphabet20=$(printf ${p20_start_raw:0:1})
ASCIIcode20=$(printf "%02d" \"${alphabet20})
p20_start=$((${ASCIIcode20} - 65 - 8 + ${p20_start_raw:1}*8))


################## pre-dispense excute ####################
python3 shoda6/automatic_spotassay/ot2_execute/compiler/compile_predispense.py ${target_dir}/predispense_spotassay.py $num_spot $p300_start $p20_start
# transfer the pre-dispense protocol to OT-2
OT2_SSH_KEY=$HOME/.ssh/ot2_ssh_key
# varify IP address as your environment
OT2_IP_ADDRESS=192.168.11.40
protocol_to_send=${target_dir}/predispense_spotassay.py
scp -i ${OT2_SSH_KEY} ${protocol_to_send} root@${OT2_IP_ADDRESS}:/data/user_storage/spotassay/predispense_spotassay.py
# EXECUTE the predispense protocol bia ssh control
PROTOCOL_BASE=predispense_spotassay.py
ssh -i ${OT2_SSH_KEY} root@${OT2_IP_ADDRESS} "source /etc/profile && cd /data/user_storage/spotassay && opentrons_execute ${PROTOCOL_BASE}"


################# (manual) measure OD620 with byonoy Absorbance96 ##############
echo "pick up 96well plate and measure OD 620nm with byonoy"
echo -e "\n"
echo "save result csv as 'OD620.csv' in file name in the current directry {Y-MD-HMS}_spotassay"
echo -e "\n"
echo "When all tasks have been done, type d/D"
echo -e "\n"

CSV="OD620.csv"
while [ ! -e $CSV ]
do
  echo "File not exists."
  echo -e "\n"
  echo "save result csv as 'OD620.csv, and then type d/D"
  echo -e "\n"
  read D
done
  
echo -n write "well done!"
echo -e "\n"

##################### spot assay #####################
# making recipe and spot assay protocol
p300_second=$((${p300_start} + 1))
p20_second=${p20_start}
python3 shoda6/automatic_spotassay/ot2_execute/compiler/recipe_spotassay.py ${target_dir}/OD620.csv $num_spot recipe_spotassay.csv
# execute compile_protocol_spotassay_biological-test.py (serial No4 is dH20 as negative control)
python3 shoda6/automatic_spotassay/ot2_execute/compiler/compile_after_plate_reader_for_paper.py ${target_dir}/spotassay.py $num_spot $num_plate $p300_second $p20_second $weight_plate1 $weight_plate2 $weight_plate3 $weight_plate4

## transfer the protocol to OT-2
protocol_to_send=${target_dir}/spotassay.py
recipe_to_send=${target_dir}/recipe_spotassay.csv
OT2_SSH_KEY=$HOME/.ssh/ot2_ssh_key
OT2_IP_ADDRESS=192.168.11.40
scp -i ${OT2_SSH_KEY} ${protocol_to_send} root@${OT2_IP_ADDRESS}:/data/user_storage/spotassay/spotassay.py
scp -i ${OT2_SSH_KEY} ${recipe_to_send} root@${OT2_IP_ADDRESS}:/data/user_storage/spotassay/recipe_spotassay.csv

# EXECUTE order spot assay
PROTOCOL_BASE=spotassay.py
ssh -i ${OT2_SSH_KEY} root@${OT2_IP_ADDRESS} "source /etc/profile && cd /data/user_storage/spotassay && opentrons_execute ${PROTOCOL_BASE}"

