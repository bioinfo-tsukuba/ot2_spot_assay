# Automatic spotassay
automation of yeast spot assay with Opentrons OT-2.
See our paper for executing automatic spot assay.

## Requirements
1. Opentrons OT-2 (P20 GEN2 single pipette and P300 GEN2 single pipette were set.) 
2. Opentrons p300 tip rack
3. Opentrons p20 tip rack
4. byonoy Absorbance96
5. 3D Printer
6. 3D printer filament
7. Desktop computer or Raspberry Pi (for executing time-lapse scanning)
8. Flatbed scanner

# Creating labware with a 3D printer
Print STL files in the CAD directory.
- Four Petri dish mounts named petri_dish_mount.stl
- One tube rack named tuberack_50mlx4_15mlx8.stl

# Creating conda environment and installing packages in laptop computer (e.g. Macbook)
Execute in Terminal App
`conda create -n autospot --file requirements.txt`

# Executing spot assay
`sh "shoda6/automatic_spotassay_pub/ot2_execute/run_spotassay.sh"`

# Executing time-lapse scanning
After spot assay is finished, set agar plates onto a flatbed scanner in a incubater.
And execute following command in a desktop computer connected to the scanner.
`sh "shoda6/automatic_spotassay_pub/automatic_scan/scan_90min_epson_lower.sh"`
When the spots is saturated, you can finish this program by `Ctrl + c`.

# Quantification of scanned images
Set region of interest (ROI) for each spot area.
And execute following macro in your ImageJ/Fiji app.
`shoda6/automatic_spotassay_pub/quantification_with_imageJ`

# Data analysis
Execute following ipynb files in a laptop computer.
`shoda6/automatic_spotassay_pub/data_analysis/dataframe-converter.ipynb`
`shoda6/automatic_spotassay_pub/data_analysis/vis_summary.ipynb`
