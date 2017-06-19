#################################################
# This file explains the basic workings of the 	#
# KBE tool for business jets. Please read	    #
# before use.					                #
#################################################

INDEX
1. Basic capabilities
2. Folder Structure
3. Set-Up
4. Running
5. Outputs
_____________________
1. BASIC CAPABILITIES
---------------------
This tools allows for quick sizing of a typical v-tailed business jet. Main focus lies on the
vertical tail and especially the rudder. The GUI allows for interactive manupilation of the input
variables and to save the current state. This tool will aid in the decision of materials and amount
of layers, followod by a weight estimation. It shows the stresses in the rudder using colours.
___________________
2. Folder Structure
-------------------
The current folder is the root directory and a correct installation contains the following folders
and sub-folders: 
	- bay_analysis_tool	#Contains the bay scripts
		*docs		#Bay documentation
	- bin			#Contains the program scripts
		*output		#AVL output directory
	- input			#User variables input directory
		*airfoils	#Airfoil directory
		*materials	#Material .csv directory
	- output		#General output directory
_________	*CAD		#STEP file output directory
3. Set-Up
---------
Before running the software a couple of files are required for set-up.
- At least one .dat airfoil file (samples have been provided). This must declare the airfoil
  from start to end along its perimeter, without defining the chord. 
- At least one material .csv file, adhering to the format of the sample files provided in the materials
  folder (see Folder Structure). 
- All .csv files in the Input folder containing at least all the variables that can be found in the sample
  sample files.

The user is to define all variables in the input folder files. Explanation and units can be found in the 
file itself. Please adhere to the same structure or the programme may fail. 

Note that some not often changed values may be found in the constants.csv file. Change these as you wish. 
__________
4. RUNNING 
----------
To run the software launch the 'run' file found in the root (this requires python and ParaPy). 
This will open the master script. Run this to start the analysis and this opens the ParaPy GUI. 
Make sure you run it from the root direcetory and not the bin directory.

From the parapy GUI you may view a precise analysis of the vertical tail or preview the overall spacecraft
by opening the corresponding parts. The input variables can be edited from "0" under root. 
Forces may be calculated by triggering their corresponding attributes. 
To save the current state to the JSON format trigger the attribute 'saving_it'. 
To save the rudder and/or wetted surfaces to a STEP file go into '1' under root and write either or both
of them. 

__________
5. OUTPUTS
----------
The main outputs can be viewed in the attribute section of the GUI. Saving them will be added in a next
version. 
The results of the AVL analysis can be found in the corresponding folder (see Folder Structure).
Saving the current input variables will be stored in the JSON format and can be found in their
corresponding folder. To re-run the program with those settings simply copy them to the input folder
and re-run the program.
