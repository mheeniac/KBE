from math import *
import glob
import os
from parapy.core import *
from parapy.geom import *
from fuselage import Fuselage
from wing import Wing
from wingset import Wingset
from vtailwing import VTailWing

# # Read the input variables from all .txt files in the input folder
# path='../test' # Define path for the input folder
# my_data={}      # Create empty dictionary called my_data
# for filename in glob.glob(os.path.join(path,'*txt')):   # Loop over all .txt files in  directory, create filename
#     with open(filename, 'r') as f:                      # Open the filename as read in variable f
#         for line in f:
#             if "#" not in line and line.strip() and 'NaN' not in line and '.' in line:
#                 # FLOAT
#                 # Ignore all empty lines and comment lines
#                 # Make sure there is no NaN value in the line
#                 # Check if it is a float number
#                 eq_index=line.find('=')                     # find the index for the = position in the line
#                 var_name = line[:eq_index].strip()          # Variable name is everything before the = sign
#                 number = float(line[eq_index + 1:].strip()) # Number is everything after the = sign convert to float
#                 my_data[var_name]=number                    # Append the dictionary
#             elif "#" not in line and line.strip() and 'NaN' not in line and '.' not in line:
#                 # INTEGER
#                 eq_index = line.find('=')
#                 var_name = line[:eq_index].strip()
#                 number = int(line[eq_index + 1:].strip())   # Number is everything after the = sign convert to integer
#                 my_data[var_name] = number
#             elif "#" not in line and line.strip():
#                 # STRING
#                 # This line contains the 'NaN' and should be a string
#                 eq_index = line.find('=')
#                 var_name = line[:eq_index].strip()
#                 number = str(line[eq_index + 1:].strip())
#                 my_data[var_name] = number
#
# globals().update(my_data) # Update the dictionary to globals




class Aircraft(Base):
    tail_arm_v_wing = Input(10.)

    with open("../input/input_new.txt", "r") as file:
        for line in file:
            if "#" not in line and line.strip():
                exec (line)
    with open("../input/constants_new.txt", "r") as file:
        for line in file:
            if "#" not in line and line.strip():
                exec (line)

    @Part
    def fuselage_part(self):
        return Fuselage(cabin_diameter=self.cabin_diameter,
                        cabin_length_user=self.cabin_length_user,
                        nose_slenderness=self.nose_slenderness,
                        tail_slenderness=self.tail_slenderness,
                        fuselage_slenderness=self.fuselage_slenderness,
                        upsweep_angle=self.upsweep_angle,
                        n_section=self.n_section)

    @Part(in_tree=False)
    def def_main_wing(self):
        return Wingset(w_c_root=self.main_root,
                       w_c_tip_user=self.main_w_c_tip,
                       sweep_angle_user=self.main_sweep_angle_user,
                       taper_ratio=self.main_taper_ratio,
                       dihedral_angle_user=self.main_dihedral_angle_user,
                       m_cruise=self.m_cruise,
                       TechFactor=self.main_TechFactor,
                       w_span=self.main_w_span)

    @Part(in_tree=False)
    def rotate_main_wing(self):
        return RotatedShape(shape_in=self.def_main_wing.wingset[child.index],
                            rotation_point=Point(0, 0, 0),
                            vector=Vector(1, 0, 0),
                            angle=radians(90),
                            quantify=2
                            )

    @Part(in_tree=True)
    def translate_main_wing(self):
        return TranslatedShape(shape_in=self.rotate_main_wing[child.index],
                               displacement=Vector(
                                   self.fuselage_part.length_nose + 0.6 * self.fuselage_part.cabin_length - self.def_main_wing.def_wingset.Aerodynamicpoint.x,
                                   0,
                                   self.fuselage_part.cabin_diameter / 7),
                               quantify=2
                               )

    @Part(in_tree=False)
    def def_v_tail_wing(self):
        return VTailWing(w_c_root=self.v_root,
                         w_c_tip_user=self.v_w_c_tip,
                         sweep_angle_user=self.v_sweep_angle_user,
                         taper_ratio=self.v_taper_ratio,
                         dihedral_angle_user=self.v_dihedral_angle_user,
                         m_cruise=self.m_cruise,
                         TechFactor=self.v_TechFactor,
                         w_span=self.v_w_span,
                         d_hinge=self.d_hinge,
                         p_zero=self.p_zero,
                         p_rib=self.p_rib)

    @Part(in_tree=False)
    def translate_v_tail_wing(self):
        return TranslatedShape(shape_in=self.def_v_tail_wing.def_vwing.sld3,
                               displacement=Vector(
                                   self.fuselage_part.length_nose + 0.6 * self.fuselage_part.cabin_length + self.tail_arm_v_wing - self.def_v_tail_wing.def_vwing.Aerodynamicpoint.x,
                                   0,
                                   self.fuselage_part.cabin_diameter / 2)
                               )

    @Part(in_tree=False)
    def def_h_tail_wing(self):
        return Wingset(w_c_root=5.,
                       w_span=8.,
                       dihedral_angle_user=0
                       )

    @Part(in_tree=False)
    def rotate_h_tail_wing(self):
        return RotatedShape(shape_in=self.def_h_tail_wing.wingset[child.index],
                            rotation_point=Point(0, 0, 0),
                            vector=Vector(1, 0, 0),
                            angle=radians(90),
                            quantify=2
                            )

    @Part(in_tree=False)
    def translate_h_tail_wing(self):
        return TranslatedShape(shape_in=self.rotate_h_tail_wing[child.index],
                               displacement=Vector(
                                   self.fuselage_part.length_nose + 0.6 * self.fuselage_part.cabin_length + self.tail_arm_v_wing - self.def_v_tail_wing.def_vwing.Aerodynamicpoint.x + self.def_v_tail_wing.def_vwing.w_sweep,
                                   0,
                                   self.fuselage_part.cabin_diameter / 2 + self.def_v_tail_wing.w_span),
                               quantify=2
                               )

    @Attribute(in_tree=True)
    def tail_wings(self):
        return self.translate_v_tail_wing, self.translate_h_tail_wing


if __name__ == '__main__':
    from parapy.gui import display

    obj = Aircraft()
    display(obj)
