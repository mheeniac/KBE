import json
from parapy.core import *
import glob
import os


class LoadData(Base):
    path = '../input'  # Define the path for the input folder
    load_vars = {}  # Create an empty dictionary
    load_json = False  # Initialize bool value

    for filename in glob.glob(os.path.join(path, '*txt')):  # Loop over all .txt files in  directory, create filename
        if 'json' in filename:  # There is a json settings file
            load_json = True  # Set the bool to true

            with open(filename, 'r') as file:  # Open the json file
                json_str = file.read()  # Read and store in var
                load_vars = json.loads(json_str)  # Load into dictionary

        else:  # There is no json settings file
            load_json = False  # Set to false
    if load_json == False:  # There is no json settings file, use regular one
        for filename in glob.glob(
                os.path.join(path, '*_.txt')):  # Loop over all _.txt files in  directory, create filename
            with open(filename, 'r') as f:  # Open the filename as read in variable f
                for line in f:
                    if "=" in line and "#" not in line:
                        # Only takes lines with variables in them
                        if 'NaN' in line or '.dat' in line or '.csv' in line:
                            # STRING
                            # This is either a NaN value or a file name
                            eq_index = line.find('=')  # find the index for the = position in the line
                            var_name = line[:eq_index].strip()  # Variable name is everything before the = sign
                            number = str(
                                line[eq_index + 1:].strip())  # Number is everything after the = sign convert to float
                            load_vars[var_name] = number  # Append the dictionary
                        elif '.' in line:
                            # FLOAT
                            # These are all floats (numbers with a '.')
                            eq_index = line.find('=')
                            var_name = line[:eq_index].strip()
                            number = float(line[eq_index + 1:].strip())
                            load_vars[var_name] = number
                        else:
                            # INTEGER
                            # All other cases are integers
                            eq_index = line.find('=')
                            var_name = line[:eq_index].strip()
                            number = int(line[eq_index + 1:].strip())
                            load_vars[var_name] = number
    globals().update(load_vars)  # Update the dictionary to globals


def save_data(obj):
    out_path = '../output'
    save_path = os.path.join(out_path,'var_output_json.txt')
    out = {}
    # Fuselage Variables
    out["cabin_diameter"] = obj.cabin_diameter
    out["cabin_length_user"] = obj.cabin_length_user
    out["nose_slenderness"] = obj.nose_slenderness
    out["tail_slenderness"] = obj.tail_slenderness
    out["upsweep_angle"] = obj.upsweep_angle
    #out["fuselage_slenderness"] = obj.fuselage_slenderness
    # Main Wing Variables
    out["main_root"] = obj.main_root
    out["main_w_c_tip"] = obj.main_w_c_tip
    out["main_sweep_angle_user"] = obj.main_sweep_angle_user
    out["main_taper_ratio"] = obj.main_taper_ratio
    out["main_dihedral"] = obj.main_dihedral
    out["m_cruise"] = obj.m_cruise
    out["main_w_span"] = obj.main_w_span
    out["m_airfoil_root"] = obj.m_airfoil_root
    out["m_airfoil_tip"] = obj.m_airfoil_tip
    # Vertical Wing
    out["v_sweep_angle_user"] = obj.v_sweep_angle_user
    out["v_taper_ratio"] = obj.v_taper_ratio
    out["v_dihedral"] = obj.v_dihedral
    out["v_w_span"] = obj.v_w_span
    out["v_airfoil_root"] = obj.v_airfoil_root
    out["v_airfoil_tip"] = obj.v_airfoil_tip
    # Horizontal Wing
    out["h_w_c_tip"] = obj.h_w_c_tip
    out["h_root"] = obj.h_root
    out["h_sweep_angle_user"] = obj.h_sweep_angle_user
    out["h_taper_ratio"] = obj.h_taper_ratio
    out["h_dihedral"] = obj.h_dihedral
    out["h_w_span"] = obj.h_w_span
    out["h_airfoil_root"] = obj.h_airfoil_root
    out["h_airfoil_tip"] = obj.h_airfoil_tip
    # AVL analysis
    out["rho"] = obj.rho
    out["FoS"] = obj.FoS
    out["Vv"] = obj.Vv
    out["Vh"] = obj.Vh
    out["rud_angle"] = obj.rud_angle
    # Forces
    out["x_fc"] = obj.x_fc
    out["ply_file_s1"] = obj.ply_file_s1
    out["n_layers_s1"] = obj.n_layers_s1
    out["n_section"] = obj.n_section
    out["n_section"] = obj.n_section
    out["main_TechFactor"] = obj.main_TechFactor
    out["v_TechFactor"] = obj.v_TechFactor
    #out["d_hinge"] = obj.d_hinge
    out["p_zero"] = obj.p_zero
    out["p_rib"] = obj.p_rib
    out["w_loc_perc"] = obj.w_loc_perc

    with open(save_path, 'w') as outfile:
        json.dump(out, outfile, indent=1)

    save_path = os.path.join(out_path, 'const_output_json.txt')
    out_const = {}
    out_const["n_section"] = obj.n_section
    out_const["main_TechFactor"] = obj.main_TechFactor
    out_const["v_TechFactor"] = obj.v_TechFactor
    #out_const["d_hinge"] = obj.d_hinge
    out_const["p_zero"] = obj.p_zero
    out_const["p_rib"] = obj.p_rib
    out_const["w_loc_perc"] = obj.w_loc_perc

    with open(save_path, 'w') as outfile:
        json.dump(out_const, outfile, indent=1)
