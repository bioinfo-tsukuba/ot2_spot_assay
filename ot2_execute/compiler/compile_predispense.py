import sys

path_output_protocol = sys.argv[1]
num_samples = sys.argv[2]
p300_START = sys.argv[3]
p20_START = sys.argv[4]

  
  
  ################################################################################
    # Make protocol
protocol = """
from io import UnsupportedOperation
from opentrons import protocol_api
import json
import pandas as pd

metadata = {
    'protocolName': 'predispense before reading plate',
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
protocol += "    pipette_300.starting_tip = tiprack_300.wells()[" + str(p300_START) +"]\n"
protocol += "    pipette_300.well_bottom_clearance.aspirate = 0\n"
protocol += "    pipette_300.well_bottom_clearance.dispense = 0\n"
protocol += "    pipette_300.flow_rate.aspirate = 100\n"
protocol += "    pipette_300.flow_rate.dispense = 100\n"
protocol += "    pipette_300.flow_rate.mix = 200\n"

#calcute agar_height for p200
protocol += "    pipette_20.starting_tip = tiprack_20.wells()[" + str(p20_START) + "]\n"
protocol += "    pipette_20.flow_rate.aspirate = 50\n"
protocol += "    pipette_20.flow_rate.dispense = 50\n"
protocol += "    pipette_20.flow_rate.blow_out = 100\n"

protocol += "    #Wells in tuberacks\n    current_tubes = ['A1', 'A2', 'B1', 'B2', 'A3', 'A4', 'A5', 'A6', 'B3','B4', 'B5', 'B6']\n\n"
protocol += "    #Wells in 96-well plate\n    current_wells = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12', 'C1', 'C2', 'C3', 'C4', 'C5','C6', 'C7', 'C8', 'C9', 'C10', 'C11', 'C12']\n\n"
protocol += "    #Wells in spots\n    current_spots = ['A1', 'A2','A3', 'A4','A5','B1', 'B2','B3', 'B4', 'B5','C1', 'C2','C3', 'C4', 'C5','D1', 'D2','D3', 'D4', 'D5','E1', 'E2','E3', 'E4', 'E5','F1', 'F2','F3', 'F4', 'F5','G1', 'G2','G3', 'G4', 'G5']\n\n"


#set variables
protocol += "    spotrownum_per_plate = " + str(num_samples) + "\n"

#Make 10-fold dilution
protocol += """
    # water dispensing for dilute
    aspirated_water = 0
    pipette_300.pick_up_tip()
    for iteration2 in range(spotrownum_per_plate):
        pipette_300.aspirate(180, tuberacks[current_tubes[0]].bottom(z=105-aspirated_water))
        pipette_300.dispense(180, plate[current_wells[iteration2]])
        pipette_300.touch_tip(plate[current_wells[iteration2]])
        pipette_300.blow_out(plate[current_wells[iteration2]])
        aspirated_water += 0.5
    pipette_300.drop_tip()
"""

with open(path_output_protocol, "w") as fw:
    n = fw.write(protocol)