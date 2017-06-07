import csv_handle as csvr
from fuselage import Fuselage
from wingset import *
#TODO:

# Read function from external file to read the .csv files
fuse = csvr.read_input("fuselage.csv")   # Fuselage Settings
const = csvr.read_input("constants.csv") # Fuselage Settings
mwing = csvr.read_input("mwing.csv")     # Fuselage Settings


class Aircraft(Base):
    # Name for the root object in the tree
    label  = 'Business Jet'

    #: cabin diameter [m]
    #: :type: float
    cabin_diameter = Input(fuse["cabin_diameter"])

    #: cabin length [m]
    #: :type: float
    cabin_length = Input(fuse["cabin_length"])

    #: fuselage nose slenderness (length over base diameter) [ratio]
    #: :type: float
    nose_slenderness = Input(fuse["nose_slenderness"])  # typical value between 1.2 and 2.5

    #: fuselage tailcone slenderness (length of base diameter) [ratio]
    #: :type: float
    tail_slenderness = Input(fuse["tail_slenderness"])  # typical between 2.5 - 5

    #: tailcone upsweep angle [degrees]
    #: :type: float
    upsweep_angle = Input(fuse["upsweep_angle"])  # typical value between 6  and 11

    #: The taper of the tail section (tip over base) [ratio]
    #: :type: float
    tail_taper = Input(fuse["tail_taper"])

    #: number circular of sections that make up the nose []
    #: :type: integer
    n_section = Input(fuse["n_section"])

    #: length of the root chord [m]
    #: :type: float
    w_c_root = Input(mwing["w_c_root"])

    #: single wing span [m]
    #: :type: float
    w_span = Input(mwing["w_span"])

    #: wing sweep angle [degrees]
    #: :type: float or str
    sweep_angle = Input(mwing["sweep_angle"])  # Overwrites default function if ~= 'NaN'

    #: wing taper ratio []
    #: :type: float or str
    taper_ratio = Input(mwing["taper_ratio"])  # Overwrites the default function if ~= 'NaN'

    #: wing dihedral angle [degrees]
    #: :type: float or str
    dihedral_angle = Input(mwing["dihedral_angle"])  # Overwrites the default function if ~= 'NaN'

    #: jet cruise speed [mach]
    #: :type: float
    m_cruise = Input(const["m_cruise"])  # Used to calculate the default sweep angle

    #: airfoil technology factor []
    #: :type: float
    TechFactor = Input(mwing["TechFactor"])  # Technology factor is equal to 0.87 NACA 6 airfoil and 1 to other conventional airfoils

    #: the name of the root airfoil file
    #: :type: string
    airfoil_root = Input(mwing["airfoil_root"])

    #: the name of the tip airfoil file
    #: :type: string
    airfoil_tip = Input(mwing["airfoil_tip"])

    #: Percentile location of the main wing aerodynamic center of the cabin length
    #: :type: float
    w_loc_perc = Input(mwing["w_loc_perc"])


    @Part
    def fuselage_part(self):
        # Create a part from the fuselage class
        return Fuselage(cabin_diameter=self.cabin_diameter,
                        cabin_length=self.cabin_length,
                        nose_slenderness=self.nose_slenderness,
                        tail_slenderness=self.tail_slenderness,
                        upsweep_angle=self.upsweep_angle,
                        tail_taper = self.tail_taper,
                        n_section=self.n_section)


    @Part(in_tree=False)
    def obj_main_wing(self):
        # Create a wing object for the main wings of the plane from the wingset class
        return Wingset(w_c_root=self.w_c_root,
                       sweep_angle_user=self.sweep_angle,
                       taper_ratio_user=self.taper_ratio,
                       dihedral_angle_user=self.dihedral_angle,
                       m_cruise=self.m_cruise,
                       TechFactor=self.TechFactor,
                       w_span=self.w_span,
                       airfoil_root=self.airfoil_root,
                       airfoil_tip=self.airfoil_tip,
                       )

    @Part(in_tree=False)
    def rotate_main_wing(self):
        # Rotate the wing solids so tha tit is aligned with the fuselage
        return RotatedShape(shape_in=self.obj_main_wing.wingset[child.index],
                            rotation_point=Point(0, 0, 0),
                            vector=Vector(1, 0, 0),
                            angle=radians(-90),
                            quantify=2
                            )

    @Part(in_tree=True)
    def main_wing(self):
        # Translate the wings such that the aerodynamic center is at 60% of the cabin length
        return TranslatedShape(shape_in=self.rotate_main_wing[child.index],
                               displacement=Vector(
                                   self.adc_diff, # Translate along fuselage length with calculated difference
                                   0,
                                   self.fuselage_part.cabin_diameter / 7), # Translate down so that it is bottom wing
                               quantify=2,
                               color = 'red',
                               label = ['Left Wing', 'Right Wing'][child.index]
                               )

    @Attribute(in_tree=False)
    def adc_diff(self):
        """
        Calculate the distance between the ADC and the 60% fuselage length
        :rtype: float
        """
        return self.cabin_length * (self.w_loc_perc / 100.) - self.adc_point[0] + self.fuselage_part.length_nose

    @Part(in_tree=False)
    def adc_point(self):
        """
        Create a point for the aerodynamic centre
        :rtype: Point
        """
        return Point(0.25 * self.w_c_root + self.obj_main_wing.mac_def[0],
                     0,
                     0)
    @Part
    def mac_line(self):
        """
        Create the line for the mean aerodynamic chord in the fuselage body
        :rtype: LineSegment
        """
        return LineSegment(start=Point(0.25 * self.w_c_root + self.obj_main_wing.mac_def[0] - \
                                       0.25 * self.obj_main_wing.mac_def[2],
                                       0,
                                       0),
                           end=Point(0.25 * self.w_c_root + self.obj_main_wing.mac_def[0] + \
                                     0.75 * self.obj_main_wing.mac_def[2],
                                     0,
                                     0),
                           hidden=True)

    @Part
    def trans_mac_line(self):
        """
        Translated the mean aerodynamic chord along the length of the fuselage
        :rtype: TranslatedCurve
        """
        return TranslatedCurve(curve_in=self.mac_line,
                               displacement=Vector(self.adc_diff,
                                                   0,
                                                   0.5 * self.cabin_diameter),
                               color='black',
                               line_thickness=3,
                               label='Main Wing MAC')

#     #
#     # @Part(in_tree=True)
#     # def def_v_tail_wing(self):
#     #     return VTailWing(settings = '')
#     #
#     # @Part(in_tree=False)
#     # def translate_v_tail_wing(self):
#     #     return TransformedShape(shape_in=self.def_v_tail_wing.def_vwing.sld3,
#     #                             from_position=Point(0, 0, 0),
#     #                             to_position=Point(
#     #                                 -self.h_adc_diff + (
#     #                                     self.def_v_tail_wing.def_vwing.w_c_tip - self.def_v_tail_wing.def_vwing.w_c_root),
#     #                                 0,
#     #                                 self.cabin_diameter)
#     #                             )
#     #
#     # @Part(in_tree=False)
#     # def translate_v_tail_fixed(self):
#     #     return TransformedShape(shape_in=self.def_v_tail_wing.fixed_part,
#     #                             from_position=Point(0, 0, 0),
#     #                             to_position=Point(
#     #                                 -self.h_adc_diff + (
#     #                                     self.def_v_tail_wing.def_vwing.w_c_tip - self.def_v_tail_wing.def_vwing.w_c_root),
#     #                                 0,
#     #                                 self.cabin_diameter)
#     #                             )
#     #
#     # @Part(in_tree=False)
#     # def translate_v_tail_rudder_skin(self):
#     #     return TransformedShape(shape_in=self.def_v_tail_wing.skins_rudder,
#     #                             from_position=Point(0, 0, 0),
#     #                             to_position=Point(
#     #                                 -self.h_adc_diff + (
#     #                                     self.def_v_tail_wing.def_vwing.w_c_tip - self.def_v_tail_wing.def_vwing.w_c_root),
#     #                                 0,
#     #                                 self.cabin_diameter)
#     #                             )
#     #
#     # @Part(in_tree=False)
#     # def rotated_v_tail_rudder(self):
#     #     return RotatedShape(shape_in=self.translate_v_tail_rudder_skin,
#     #                         rotation_point=Point(self.def_v_tail_wing.hingerib_line.point1.x + (-self.h_adc_diff + (
#     #                                     self.def_v_tail_wing.def_vwing.w_c_tip - self.def_v_tail_wing.def_vwing.w_c_root)),
#     #                                              self.def_v_tail_wing.hingerib_line.point1.y,
#     #                                              self.def_v_tail_wing.hingerib_line.point1.z + self.cabin_diameter),
#     #                         vector=self.def_v_tail_wing.hingerib_line.direction_vector,
#     #                         angle=radians(30))
#     #
#     # @Attribute(in_tree=False)
#     # def total_length(self):
#     #     return self.fuselage_part.fuselage_length
#     #
#     # @Part(in_tree=False)
#     # def def_h_tail_wing(self):
#     #     return Wingset(w_c_root=self.h_root,
#     #                    sweep_angle_user=self.h_sweep_angle_user,
#     #                    taper_ratio_user=self.h_taper_ratio_user,
#     #                    dihedral_angle_user=self.h_dihedral,
#     #                    m_cruise=self.m_cruise,
#     #                    TechFactor=self.h_TechFactor,
#     #                    w_span=self.h_w_span,
#     #                    airfoil_root=self.h_airfoil_root,
#     #                    airfoil_tip=self.h_airfoil_tip)
#     #
#     # @Part(in_tree=False)
#     # def rotate_h_tail_wing(self):
#     #     return RotatedShape(shape_in=self.def_h_tail_wing.wingset[child.index],
#     #                         rotation_point=Point(0, 0, 0),
#     #                         vector=Vector(1, 0, 0),
#     #                         angle=radians(90),
#     #                         quantify=2
#     #                         )
#     #
#     # @Part(in_tree=False)
#     # def translate_h_tail_wing(self):
#     #     return TranslatedShape(shape_in=self.rotate_h_tail_wing[child.index],
#     #                            displacement=Vector(
#     #                                -self.h_adc_diff,
#     #                                0,
#     #                                self.fuselage_part.cabin_diameter + self.def_v_tail_wing.w_span),
#     #                            quantify=2
#     #                            )
#     #
#     # @Attribute(in_tree=False)
#     # def tail_wings(self):
#     #     return self.translate_v_tail_wing, self.translate_h_tail_wing
#     #

#     # @Part
#     # def trans_adc_point(self):
#     #     return TranslatedShape(shape_in=self.adc_point,
#     #                            displacement=Vector(self.adc_diff,
#     #                                                0,
#     #                                                0.5 * self.cabin_diameter),
#     #                            label='Main Wing Aerodynamic Centre')
#     #
#     # @Part
#     # def h_mac_line(self):
#     #     return LineSegment(start=Point(0.25 * self.h_root + self.def_h_tail_wing.mac_def[0] - \
#     #                                    0.25 * self.def_h_tail_wing.mac_def[2],
#     #                                    0,
#     #                                    0),
#     #                        end=Point(0.25 * self.h_root + self.def_h_tail_wing.mac_def[0] + \
#     #                                  0.75 * self.def_h_tail_wing.mac_def[2],
#     #                                  0,
#     #                                  0),
#     #                        hidden=True)
#     #
#     # @Part(in_tree=False)
#     # def h_adc_point(self):
#     #     return Point(0.25 * self.h_root + self.def_h_tail_wing.mac_def[0],
#     #                  0,
#     #                  0)
#     #
#     # @Attribute(in_tree=False)
#     # def h_adc_diff(self):
#     #     # Calculate the distance between the v ADC and the main wing ADC
#     #     return self.h_adc_point[0] - self.adc_diff - self.l_h  # 15 = tail arm distance tbd from volume ratio thing
#     #
#     # @Part
#     # def trans_h_mac_line(self):
#     #     return TranslatedCurve(curve_in=self.h_mac_line,
#     #                            displacement=Vector(-self.h_adc_diff,
#     #                                                0,
#     #                                                0.5 * self.cabin_diameter),
#     #                            color='red',
#     #                            line_thickness=3,
#     #                            label='Horizontal Tail MAC')
#     #
#     # @Part
#     # def trans_h_adc_point(self):
#     #     return TranslatedShape(shape_in=self.h_adc_point,
#     #                            displacement=Vector(-self.h_adc_diff,
#     #                                                0,
#     #                                                0.5 * self.cabin_diameter),
#     #                            label='Horizontal Tail Aerodynamic Centre')
#     #
#     # @Part(in_tree=False)
#     # def v_mac_line(self):
#     #     return LineSegment(start=Point(0.25 * self.def_v_tail_wing.w_c_root + self.def_v_tail_wing.mac_def[0] - \
#     #                                    0.25 * self.def_v_tail_wing.mac_def[2],
#     #                                    0,
#     #                                    self.def_v_tail_wing.mac_def[1]),
#     #                        end=Point(0.25 * self.def_v_tail_wing.w_c_root + self.def_v_tail_wing.mac_def[0] + \
#     #                                  0.75 * self.def_v_tail_wing.mac_def[2],
#     #                                  0,
#     #                                  self.def_v_tail_wing.mac_def[1]),
#     #                        hidden=False)
#     #
#     # @Attribute(in_tree=True)
#     # def tail_wing(self):
#     #     return self.translate_v_tail_fixed, self.rotated_v_tail_rudder, self.translate_h_tail_wing
#     #
#     # @Part(in_tree=False)
#     # def v_adc_point(self):
#     #     return Point(0.25 * self.def_v_tail_wing.w_c_root + self.def_v_tail_wing.mac_def[0],
#     #                  0,
#     #                  self.def_v_tail_wing.mac_def[1])
#     #
#     # @Attribute(in_tree=False)
#     # def l_h(self):
#     #     l_h = (self.Vh * self.obj_main_wing.ref_area * self.obj_main_wing.mac_def[2]) / self.def_h_tail_wing.ref_area
#     #     return l_h
#     #
#     # @Part
#     # def trans_v_mac_line(self):
#     #     return TranslatedCurve(curve_in=self.v_mac_line,
#     #                            displacement=Vector(-self.h_adc_diff + (
#     #                                self.def_v_tail_wing.def_vwing.w_c_tip - self.def_v_tail_wing.def_vwing.w_c_root),
#     #                                                0,
#     #                                                self.cabin_diameter),
#     #                            color='blue',
#     #                            line_thickness=3,
#     #                            label='Vertical Tail MAC')
#     #
#     # @Part
#     # def trans_v_adc_point(self):
#     #     return TranslatedShape(shape_in=self.v_adc_point,
#     #                            displacement=Vector(-self.h_adc_diff + (
#     #                                self.def_v_tail_wing.def_vwing.w_c_tip - self.def_v_tail_wing.def_vwing.w_c_root),
#     #                                                0,
#     #                                                self.cabin_diameter),
#     #                            label='Vertical Tail Aerodynamic Centre')
#     #
#     # @Attribute
#     # def saving_it(self):
#     #     save_data(self)
#     #     return 'SaveData'
#     #
#     # @Part
#     # def interface(self):
#     #     return avl.Interface(filename="FullAircraft",
#     #                          directory="output",
#     #                          geometry=geometry(self),
#     #                          outputs=["fs", "fn", "fe"],
#     #                          close_when_done=True,
#     #                          if_exists="overwrite"
#     #                          )
#     #
#     # @Attribute
#     # def hinge_side_force(self):
#     #     Cy_dict = self.interface.surface_forces  # Create dictionary from AVL
#     #     Cy = Cy_dict["surfaces"]["Rudder"]["CY"]  # Side force coefficient
#     #     S_ref = Cy_dict["surfaces"]["Rudder"]["Ssurf"]  # Reference area
#     #     q_dyn = 0.5 * self.rho * (self.m_cruise * 340) ** 2  # Dynamic pressure
#     #     Fy = Cy * q_dyn * self.obj_main_wing.ref_area * self.FoS  # Side Force
#     #     q = Fy / self.def_v_tail_wing.b_rudder  # Distributed Load
#     #     return Fy, q
#     #
#     # @Attribute
#     # def hinge_mass(self):
#     #     h = self.def_v_tail_wing.d_front_spar * 1000  # in mm
#     #     weight = []
#     #     for x in range(0,len(self.hinge_reaction_forces[0])):
#     #         mass = 0.110 * (1 + (abs(self.hinge_reaction_forces[0][x]) / 30000)) * ((h/100) + 1)
#     #         weight.append(mass)
#     #     return weight
#     #
#     # @Attribute
#     # def hinge_reaction_forces(self):
#     #     """calculates the reaction forces per hinge [N]
#     #            :rtype: list
#     #     """
#     #     q = self.hinge_side_force[1]  # The distributed load
#     #     R = []  # An empty list
#     #     l = []  # An empty list
#     #     for x in range(0, len(self.def_v_tail_wing.hinges)):
#     #         if x == 0:
#     #             p2_z = self.def_v_tail_wing.hinges[x].position.z
#     #             p1_z = self.def_v_tail_wing.fixed_part.position.z
#     #             p3_z = self.def_v_tail_wing.hinges[x + 1].position.z
#     #             pmid_z = p3_z - 0.5 * (p3_z - p2_z)
#     #             length = pmid_z - p1_z
#     #             l.append(length)
#     #             force = q * length
#     #             R.append(force)
#     #         elif x > 0 and x < (len(self.def_v_tail_wing.hinges) - 1):  # All the middle hinges
#     #             p1_z = pmid_z  # Take the previous midpoint and set it as bottom
#     #             p2_z = self.def_v_tail_wing.hinges[x].position.z  # Take the position of current hinge
#     #             p3_z = self.def_v_tail_wing.hinges[x + 1].position.z  # Take position of the next hinge
#     #             pmid_z = p3_z - 0.5 * (p3_z - p2_z)  # Position middle of current and next hinge
#     #             length = pmid_z - p1_z  # Length is current middle - last middle
#     #             l.append(length)  # Append length list
#     #             force = q * length
#     #             R.append(force)
#     #         elif x == (len(self.def_v_tail_wing.hinges) - 1):
#     #             length = self.def_v_tail_wing.b_rudder - pmid_z  # The length of the last part, total - last mid
#     #             l.append(length)  # Append lengths
#     #             force = q * length  # Calculate force
#     #             R.append(force)  # Append force
#     #     check = (sum(l) - self.def_v_tail_wing.b_rudder == 0)  # Checks if the calculations of l are valid
#     #
#     #     return R, check, q, force
#     #
#     # @Attribute
#     # def actuator_forces(self):
#     #     """ Calculates the actuator force [N]
#     #                   :rtype: float
#     #     """
#     #     d_hl = self.def_v_tail_wing.d_hinge * self.x_fc  # arm over which force F acts
#     #     M_f = self.hinge_side_force[0] * d_hl  # Moment due to side force
#     #     point_act = self.def_v_tail_wing.actuator_hinge_line.midpoint  # Point on act line
#     #     point_hinge = self.def_v_tail_wing.hingerib_line.midpoint  # point on hinge line
#     #     point_act = Point(point_act.x, point_act.y, 0)  # Strip z location
#     #     point_hinge = Point(point_hinge.x, point_hinge.y, 0)  # Strip z location
#     #     da = point_act.distance(point_hinge)  # Distance between lines
#     #     Fa = M_f / da  # The actuator Force [N]
#     #     Fa_x = Fa * cos(radians(self.rud_angle))
#     #     Fa_y = Fa * sin(radians(self.rud_angle))
#     #     distance = self.force_distances
#     #     F1 = Fa * distance[0][1] / sum(distance[0])  # Force on nearest hinge
#     #     F1_x = F1 * cos(radians(self.rud_angle))
#     #     F1_y = F1 * sin(radians(self.rud_angle))
#     #     F2 = Fa * distance[0][0] / sum(distance[0])  # Force on second nearest hinge
#     #     F2_x = F2 * cos(radians(self.rud_angle))
#     #     F2_y = F2 * sin(radians(self.rud_angle))
#     #     Fh = [[F1_x, F1_y], [F2_x, F2_y], distance[1]]  # Forces and their corresponding hinge numbers
#     #     return [Fa_x, Fa_y], Fh, M_f
#     #
#     # @Attribute
#     # def force_distances(self):
#     #     """ Calculates the distance between the actuator force and the nearest two hinges
#     #                   :rtype: float
#     #     """
#     #     force_point = self.def_v_tail_wing.actuator_hinge_line.midpoint
#     #     distances = []
#     #     for x in range(0, len(self.def_v_tail_wing.hinges)):
#     #         dist = force_point.distance(self.def_v_tail_wing.hinges[x].position)
#     #         distances.append(dist)
#     #     shortest = sorted(distances)[0:2]  # Finds the shortest two distances
#     #     hinge_number = []
#     #     hinge_number.append(distances.index(shortest[0]))  # Find the hinge number of the first distance
#     #     hinge_number.append(distances.index(shortest[1]))  # Find the hinge number of the second distance
#     #     return shortest, hinge_number
#     #
#     # @Attribute
#     # def gen_material(self):
#     #     generate = ReadMaterial(ply_file=self.ply_file,
#     #                             n_layers=self.n_layers)
#     #     dict_mat = generate.read
#     #     return dict_mat
#     #
#     # @Attribute
#     # def planes(self):
#     #     p2_z = self.def_v_tail_wing.hinges[0].position.z
#     #     p1_z = self.def_v_tail_wing.fixed_part.position.z
#     #     plane2 = TranslatedPlane(built_from=self.def_v_tail_wing.rudder_plns.first,
#     #                              displacement=Vector(0, 0, 0.02))
#     #     plane1 = TranslatedPlane(built_from=plane2,
#     #                              displacement=Vector(0, 0, p2_z - p1_z))
#     #     return plane1, plane2
#     #
#     # @Attribute
#     # def rhs_skin_faces(self):
#     #     return self.def_v_tail_wing.fused_le_skin_right, self.def_v_tail_wing.main_skin_right, self.def_v_tail_wing.te_skin_right
#     #
#     # @Attribute
#     # def lhs_skin_faces(self):
#     #     return self.def_v_tail_wing.fused_le_skin_left, self.def_v_tail_wing.main_skin_left, self.def_v_tail_wing.te_skin_left
#     #
#     # @Attribute
#     # def spar_faces(self):
#     #     return self.def_v_tail_wing.rudder_front_spar, self.def_v_tail_wing.rudder_back_spar
#     #
#     # @Attribute
#     # def ref_x(self):
#     #     x1 = self.def_v_tail_wing.rudder_plns.last.reference.z
#     #     x2 = self.def_v_tail_wing.rudder_plns.first.reference.z
#     #     return x1, x2
#     #
#     # @Attribute
#     # def ref_y(self):
#     #     z_hinge = self.def_v_tail_wing.p_zero + self.def_v_tail_wing.p_rib * (
#     #         self.def_v_tail_wing.pick_hingeribs[0] - 1)
#     #     z_1 = self.ref_x[0]
#     #     z_2 = self.ref_x[1]
#     #     y_pos_root_begin = self.fixed_part_with_ribs.vertices[25 - 2 * self.pick_hingeribs[0]].point
#     #     y_pos_root_end = self.fixed_part_with_ribs.vertices[24 - 2 * self.pick_hingeribs[0]].point
#     #     points = [y_pos_root_begin, y_pos_root_end]
#     #     distance = Point.distance(*points)
#     #     y1 = y_pos_root_begin.y + distance * self.def_v_tail_wing.rhl_root + (
#     #                                                                              self.def_v_tail_wing.hingerib_line.direction_vector.y / self.def_v_tail_wing.hingerib_line.direction_vector.z) * (
#     #                                                                              z_1 - z_hinge)
#     #     y2 = y_pos_root_begin.y + distance * self.def_v_tail_wing.rhl_root + (
#     #                                                                              self.def_v_tail_wing.hingerib_line.direction_vector.y / self.def_v_tail_wing.hingerib_line.direction_vector.z) * (
#     #                                                                              z_2 - z_hinge)
#     #     return y1, y2
#     #
#     # @Attribute
#     # def forces(self):
#     #     p2_z = self.def_v_tail_wing.hinges[0].position.z
#     #     p1_z = self.def_v_tail_wing.fixed_part.position.z
#     #     q = self.hinge_reaction_forces[2]
#     #     R = self.hinge_reaction_forces[0][0]
#     #     FX = [0, self.actuator_forces[0][0]]
#     #     FY = [0, q * (p2_z - p1_z) - R]
#     #     MX = [0, q * (p2_z - p1_z) * (p2_z - p1_z)]
#     #     MY = [0, 0]
#     #     MZ = [0, q * (p2_z - p1_z)]
#     #     return FX, FY, MX, MY, MZ
#     #
#     # @Attribute
#     # def bay_analysis(self):
#     #     skin_1 = ReadMaterial(ply_file=self.ply_file_s1, n_layers=self.n_layers_s1)
#     #     skin_1 = skin_1.read
#     #     bay_ana = BayAnalysis(Vx=self.forces[0],
#     #                           Vy=self.forces[1],
#     #                           Mx=self.forces[2],
#     #                           My=self.forces[3],
#     #                           Mt=self.forces[4],
#     #                           ref_x=[0] * 2,
#     #                           ref_y=[0] * 2,
#     #                           bay_planes=self.planes,
#     #                           rhs_skin_faces=self.rhs_skin_faces,
#     #                           lhs_skin_faces=self.lhs_skin_faces,
#     #                           spar_faces=self.spar_faces,
#     #                           rhs_skin_materials_t=[skin_1['t']] * 3,
#     #                           lhs_skin_materials_t=[skin_1['t']] * 3,
#     #                           spar_materials_t=[skin_1['t']] * 2,
#     #                           rhs_skin_materials_E=[skin_1['E']] * 3,
#     #                           lhs_skin_materials_E=[skin_1['E']] * 3,
#     #                           spar_materials_E=[skin_1['E']] * 2,
#     #                           rhs_skin_materials_G=[skin_1['G']] * 3,
#     #                           lhs_skin_materials_G=[skin_1['G']] * 3,
#     #                           spar_materials_G=[skin_1['G']] * 2,
#     #                           rhs_skin_materials_D=[[skin_1['D11'], skin_1['D22'], skin_1['D22'], skin_1['D12']]] * 3,
#     #                           lhs_skin_materials_D=[[skin_1['D11'], skin_1['D22'], skin_1['D22'], skin_1['D12']]] * 3,
#     #                           spar_materials_D=[[skin_1['D11'], skin_1['D22'], skin_1['D22'], skin_1['D12']]] * 2,
#     #                           N=3)
#     #     return bay_ana
#     #
#     # @Part(in_tree=False)
#     # def fuse_fuselage(self):
#     #     return FusedSolid(shape_in=self.fuselage_part.RotatedMainSolid[1],
#     #                       tool=[self.fuselage_part.RotatedMainSolid[0], self.fuselage_part.RotatedMainSolid[2]])
#     #
#     # @Part(in_tree=False)
#     # def wet_wings_left(self):
#     #     return SubtractedSolid(shape_in=self.main_wing[0],
#     #                            tool = self.fuse_fuselage)
#     # @Part(in_tree=False)
#     # def wet_wings_right(self):
#     #     return SubtractedSolid(shape_in=self.main_wing[1],
#     #                            tool = self.fuse_fuselage)
#     #
#     #
#     #
#     #
#     # @Part(in_tree=False)
#     # def get_parts(self):
#     #     return Aircraft()
#     #
#     # @Attribute
#     # def rudder_nodes(self):
#     #     tail = self.get_parts.def_v_tail_wing
#     #
#     #     list = [tail.skins_rudder,
#     #             tail.rudder_back_spar,
#     #             tail.rudder_front_spar,
#     #             tail.actuator_hinge_line,
#     #             tail.hingerib_line,
#     #             tail.closure_ribs[0],
#     #             tail.closure_ribs[1],
#     #             tail.actuator_hinges[0],
#     #             tail.actuator_hinges[1]]
#     #     for x in range(0, len(tail.find_mainskin_ribs)):
#     #         list.append(tail.find_mainskin_ribs[x])
#     #     for x in range(0, len(tail.hinges)):
#     #         list.append(tail.hinges[x])
#     #     return list
#     #
#     # @Part
#     # def rudder_writer(self):
#     #     return STEPWriter(nodes=self.rudder_nodes,
#     #                       default_directory='../output/CAD')
#     # @Attribute
#     # def wetted_nodes(self):
#     #     list = [self.get_parts.tail_wing[0],
#     #             self.get_parts.tail_wing[1],
#     #             self.get_parts.tail_wing[2][0],
#     #             self.get_parts.tail_wing[2][1],
#     #             self.get_parts.fuse_fuselage,
#     #             self.get_parts.wet_wings_left,
#     #             self.get_parts.wet_wings_right]
#     #
#     #     return list
#     # @Part
#     # def wetted_writer(self):
#     #     return STEPWriter(nodes=self.wetted_nodes,
#     #                       default_directory='../output/CAD')
#     @Attribute
#     def save_vars(self):
#         path = self.read.generate_path
#         first_row = True
#         with open(path[0], 'rb') as file:  # Open file
#             reader = csv.reader(file, delimiter=',', quotechar='|')  # Read into reader and section rows and columns
#             with open(path[1], 'wb') as outfile:
#                 filewriter = csv.writer(outfile, delimiter=',', quotechar='|')
#                 for row in reader:
#                     if first_row == True:
#                         filewriter.writerow(row)
#                         first_row = False
#                     else:
#                         # Find the name of the variable that we want to request and save
#                         var_name = row[0]
#                         value = getattr(self, var_name)
#                         # Update the value in row
#                         row[1] = value
#                         # Write the row to a new file
#                         filewriter.writerow(row)
#         return 'Saved'
#
if __name__ == '__main__':
    from parapy.gui import display

    obj = Aircraft()
    display(obj)
