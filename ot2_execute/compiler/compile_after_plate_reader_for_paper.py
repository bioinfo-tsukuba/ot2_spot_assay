from numpy import append
import pandas as pd
import sys
import math
from pandas.io.parsers import read_csv

# Parse arguments
path_output_protocol = sys.argv[1]

num_samples = int(sys.argv[2])
num_dishes = int(sys.argv[3])

agar_height_array=list()
for i in range(num_dishes):
    agarANDdish_weight = float(sys.argv[6+i])
    agar_weight = agarANDdish_weight-17.88
    agar_density = 0.00102 #g/mm^3
    dish_diameter = 86
    agar_height = round(agar_weight/((math.pi*(dish_diameter/2)**2)*agar_density), 1)  #calculate native agar height(cm)
    agar_height_array.append(agar_height+3)  #plus the bottom thickness of dish (3mm) and make array data for adapting some different dishes

p300_START = int(sys.argv[4])
p20_START = int(sys.argv[5])


    ################################################################################
    # Make protocol

protocol = """
from io import UnsupportedOperation
from opentrons import protocol_api
import json
import math
import pandas as pd
import slackweb
import os

metadata = {
    'protocolName': 'Execute Spot Assay',
    'author': 'Shodai Taguchi <taguchi.shodai.td@alumni.tsukuba.ac.jp>',
    'apiLevel': '2.0'
}
"""
protocol += """
def run(protocol: protocol_api.ProtocolContext):
    
    # Labware
    tiprack_300   = protocol.load_labware('opentrons_96_tiprack_300ul', '1')
    tiprack_20   = protocol.load_labware('opentrons_96_tiprack_20ul', '4')
    plate     = protocol.load_labware('corning_96_wellplate_360ul_flat', '3')
    with open("/data/user_storage/labware/tuberack_50mm-x4_15mm-x8.json") as tuberacks_load:
        tuberacks_def = json.load(tuberacks_load)
        tuberacks = protocol.load_labware_from_definition(tuberacks_def, '2')
    with open("/data/user_storage/labware/90mm_dish/20220131_90mm_dish_usonic.json") as dish_spot_assay:
        dish_def = json.load(dish_spot_assay)
        dish0 = protocol.load_labware_from_definition(dish_def, '5')
        dish1 = protocol.load_labware_from_definition(dish_def, '6')
        dish2 = protocol.load_labware_from_definition(dish_def, '8')
        dish3 = protocol.load_labware_from_definition(dish_def, '9')
    pipette_300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack_300])
    pipette_20 = protocol.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_20])

"""

    # Set pipette properties
protocol += "    # Set pipette properties\n"
protocol += "    pipette_300.starting_tip = tiprack_300.wells()[" + str(p300_START) + "]\n"
protocol += "    pipette_300.well_bottom_clearance.aspirate = 2\n"
protocol += "    pipette_300.well_bottom_clearance.dispense = 3\n"
protocol += "    pipette_300.flow_rate.aspirate = 100\n"
protocol += "    pipette_300.flow_rate.dispense = 100\n"
protocol += "    pipette_300.flow_rate.mix = 200\n"

    #calcute agar_height for p200
protocol += "    pipette_20.starting_tip = tiprack_20.wells()[" + str(p20_START) + "]\n"
# protocol += "    pipette_20.well_bottom_clearance.dispense = " + str(agar_height-5) + "\n"
protocol += "    pipette_20.flow_rate.aspirate = 50\n"
protocol += "    pipette_20.flow_rate.dispense = 50\n"
# protocol += "    pipette_20.well_bottom_clearance.blow_out = " + str(agar_height-4) + "\n"
protocol += "    pipette_20.flow_rate.blow_out = 100\n"

    # Wells in tuberacks
protocol += "    # Wells in tuberacks\n    current_tubes = ['A1', 'A2', 'B1', 'B2', 'A3', 'A4', 'A5', 'A6', 'B3','B4', 'B5', 'B6']\n\n"

    # 96-Wells for the current recipes
protocol += "    # Wells in 96-well plate\n    current_wells = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'C1', 'C2', 'C3', 'C4', 'C5','C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12','D1', 'D2', 'D3', 'D4', 'D5','D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12','E1', 'E2', 'E3', 'E4', 'E5','E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12','F1', 'F2', 'F3', 'F4', 'F5','F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12','G1', 'G2', 'G3', 'G4', 'G5','G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12','H1', 'H2', 'H3', 'H4', 'H5','H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12']\n\n"

    # Spots for the current recipes
protocol += "    # Wells in dish\n    current_spots = ['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5', 'C1', 'C2', 'C3', 'C4', 'C5', 'D1', 'D2', 'D3', 'D4', 'D5', 'E1', 'E2', 'E3', 'E4', 'E5', 'F1', 'F2', 'F3', 'F4', 'F5', 'G1', 'G2', 'G3', 'G4', 'G5']\n\n"


    # Define variables
protocol += "    num_dilution = 5\n"
protocol += "    spotrownum_per_plate = " + str(num_samples) + "\n"
protocol += "    well_counter = " + str(num_samples) + "\n"
protocol += "    #protocol.bundled_data('recipe_spotassay.csv')\n"
protocol += "    dilute_csv = pd.read_csv('/data/user_storage/spotassay/recipe_spotassay.csv', index_col=0)\n"



    # make colored water dispensing
protocol += """
    # add water up to 200ul of the first well of serial dilution
    aspirated_water=0
    for iteration1 in range(spotrownum_per_plate):
           # iteration1 = 3, serial dilution No3 is dH2O as negative control 
            if iteration1 = 3:
                pipette_300.pick_up_tip()
                pipette_20.pick_up_tip()

                # dispensing 160ul of water from second to fifth well of serial dilution
                for iteration1_1 in range(num_dilution):
                    if  iteration1_1 == 0:
                        pipette_300.aspirate(200-50, tuberacks[current_tubes[0]].bottom(z=100-aspirated_water))
                        pipette_300.dispense(200-50, plate[current_wells[5*iteration1+spotrownum_per_plate]])
                        pipette_300.touch_tip(plate[current_wells[5*iteration1+spotrownum_per_plate]])
                        pipette_300.blow_out(plate[current_wells[5*iteration1+spotrownum_per_plate]])
                        aspirated_water += 0.5

                    elif iteration1_1 != 0:
                        pipette_300.aspirate(160, tuberacks[current_tubes[0]].bottom(z=100-aspirated_water))
                        pipette_300.dispense(160, plate[current_wells[5*iteration1+spotrownum_per_plate + iteration1_1]])
                        pipette_300.touch_tip(plate[current_wells[5*iteration1+spotrownum_per_plate + iteration1_1]])
                        pipette_300.blow_out(plate[current_wells[5*iteration1+spotrownum_per_plate + iteration1_1]])
                        aspirated_water += 0.5

                # dispensing first well of serial dilution
                pipette_300.mix(1, 150, plate[current_wells[iteration1]], rate = 3000)
                pipette_300.aspirate(50, plate[current_wells[iteration1]])
                pipette_300.dispense(50, plate[current_wells[5*iteration1+spotrownum_per_plate]])
                pipette_300.touch_tip(plate[current_wells[5*iteration1+spotrownum_per_plate]])
                pipette_300.blow_out(plate[current_wells[5*iteration1+spotrownum_per_plate]])

                # make serial dilution one by one 
                for iteration1_2 in range(num_dilution -1):
                    pipette_300.mix(1, 150, plate[current_wells[well_counter + iteration1_2 + iteration1 * 5]], rate = 2000)
                    pipette_300.aspirate(40, plate[current_wells[well_counter + iteration1_2 + iteration1 * 5]])
                    pipette_300.dispense(40, plate[current_wells[(well_counter + iteration1_2 + iteration1 * 5) + 1]])
                    pipette_300.blow_out(plate[current_wells[(well_counter + iteration1_2 + iteration1 * 5) + 1]])   
                pipette_300.mix(1, 150, plate[current_wells[well_counter + iteration1_2 + iteration1 * 5 + 1]], rate = 2000)
                pipette_300.touch_tip(plate[current_wells[(well_counter + iteration1_2 + iteration1 * 5) + 1]])

                for iteration1_3 in range(num_dilution -1, -1, -1):
"""
for j in range(num_dishes):
    protocol += "                    pipette_20.aspirate(5, plate[current_wells[well_counter + iteration1_3 + iteration1 * 5]])\n"
    protocol += "                    pipette_20.dispense(5, dish"+str(j)+"[current_spots[iteration1_3 + iteration1 * 5]].bottom(z=" + str(agar_height_array[j]) + "))\n"
protocol += """ 
                pipette_300.drop_tip()
                pipette_20.drop_tip()
                
            # iteration1 = 3, serial dilution No3 is dH2O as negative control 
            elif iteration1 != 3:
                
                pipette_300.pick_up_tip()
                pipette_20.pick_up_tip()

                # dispensing 160ul of water from second to fifth well of serial dilution
                for iteration1_1 in range(num_dilution):
                    if  iteration1_1 == 0:
                        pipette_300.aspirate(200-round(dilute_csv.iat[0, iteration1],1), tuberacks[current_tubes[0]].bottom(z=100-aspirated_water))
                        pipette_300.dispense(200-round(dilute_csv.iat[0, iteration1],1), plate[current_wells[5*iteration1+spotrownum_per_plate]])
                        pipette_300.touch_tip(plate[current_wells[5*iteration1+spotrownum_per_plate]])
                        pipette_300.blow_out(plate[current_wells[5*iteration1+spotrownum_per_plate]])
                        aspirated_water += 0.5
                        
                    elif iteration1_1 != 0:
                        pipette_300.aspirate(160, tuberacks[current_tubes[0]].bottom(z=100-aspirated_water))
                        pipette_300.dispense(160, plate[current_wells[5*iteration1+spotrownum_per_plate + iteration1_1]])
                        pipette_300.touch_tip(plate[current_wells[5*iteration1+spotrownum_per_plate + iteration1_1]])
                        pipette_300.blow_out(plate[current_wells[5*iteration1+spotrownum_per_plate + iteration1_1]])
                        aspirated_water += 0.5

                # dispensing first well of serial dilution
                pipette_300.mix(1, 150, plate[current_wells[iteration1]], rate = 3000)
                pipette_300.aspirate(round(dilute_csv.iat[0, iteration1],1), plate[current_wells[iteration1]])
                pipette_300.dispense(round(dilute_csv.iat[0, iteration1],1), plate[current_wells[5*iteration1+spotrownum_per_plate]])
                pipette_300.touch_tip(plate[current_wells[5*iteration1+spotrownum_per_plate]])
                pipette_300.blow_out(plate[current_wells[5*iteration1+spotrownum_per_plate]])

                # make serial dilution one by one 
                for iteration1_2 in range(num_dilution -1):
                    pipette_300.mix(1, 150, plate[current_wells[well_counter + iteration1_2 + iteration1 * 5]], rate = 2000)
                    pipette_300.aspirate(40, plate[current_wells[well_counter + iteration1_2 + iteration1 * 5]])
                    pipette_300.dispense(40, plate[current_wells[(well_counter + iteration1_2 + iteration1 * 5) + 1]])
                    pipette_300.blow_out(plate[current_wells[(well_counter + iteration1_2 + iteration1 * 5) + 1]])   
                pipette_300.mix(1, 150, plate[current_wells[well_counter + iteration1_2 + iteration1 * 5 + 1]], rate = 2000)
                pipette_300.touch_tip(plate[current_wells[(well_counter + iteration1_2 + iteration1 * 5) + 1]])

                for iteration1_3 in range(num_dilution -1, -1, -1):
"""
for j in range(num_dishes):
    protocol += "                    pipette_20.aspirate(5, plate[current_wells[well_counter + iteration1_3 + iteration1 * 5]])\n"
    protocol += "                    pipette_20.dispense(5, dish"+str(j)+"[current_spots[iteration1_3 + iteration1 * 5]].bottom(z=" + str(agar_height_array[j]) + "))\n"
protocol += """ 
                pipette_300.drop_tip()
                pipette_20.drop_tip()
            
            else:
                pass
    protocol.home()

    SLACK_URL = os.environ["SLACK_URL"]
    slack = slackweb.Slack(url=SLACK_URL)
    slack.notify(text="Finished Spot Assay")
"""
    # Write protocol
with open(path_output_protocol, "w") as fw:
    n = fw.write(protocol)
