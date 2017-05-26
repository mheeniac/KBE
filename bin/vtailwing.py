from math import *

from parapy.core import *
from parapy.geom import *
from wing import Wing
import warnings
from csv_in_out import *


# TODO:
# what is /8 * 2 in r_actuator and how do we make this not hard coded?


# from bay_analysis_tool.bay_analysis import BayAnalysis


class VTailWing(Base):
    # This class creates a vertical wing including rudder

    # Read function from external file
    read = ReadInput(file_name='vtail.csv')
    # Create dict
    variables = read.read_input

    read_const = ReadInput(file_name='constants.csv')
    # Create dict
    constants = read_const.read_input

    #: length of the root chord [m]
    #: :type: float
    w_c_root = Input(variables["w_c_root"])

    #: single wing span [m]
    #: :type: float
    w_span = Input(variables["w_span"])

    #: wing sweep angle [degrees]
    #: :type: float or str
    sweep_angle_user = Input(variables["sweep_angle"])  # Overwrites default function if ~= 'NaN'

    #: wing taper ratio []
    #: :type: float or str
    taper_ratio_user = Input(variables["taper_ratio"])  # Overwrites the default function if ~= 'NaN'

    #: wing dihedral angle [degrees]
    #: :type: float or str
    dihedral_angle_user = Input(variables["dihedral_angle"])  # Overwrites the default function if ~= 'NaN'

    #: jet cruise speed [mach]
    #: :type: float
    m_cruise = Input(constants["m_cruise"])  # Used to calculate the default sweep angle

    #: airfoil technology factor []
    #: :type: float
    TechFactor = Input(variables["TechFactor"])  # Technology factor is equal to 0.87 NACA 6 airfoil and 1 to other conventional airfoils

    #: the name of the root airfoil file
    #: :type: string
    airfoil_root = Input(variables["airfoil_root"])

    #: the name of the tip airfoil file
    #: :type: string
    airfoil_tip = Input(variables["airfoil_tip"])

    # Label for the tree
    label = 'Tail Wing'

    d_hinge = Input(0.5)
    # p_zero = Input(0.25)
    # p_rib = Input(0.5)
    p_form_rib = Input(0.3)

    #: number of used hinges
    #: :type: integer
    number_hinges = Input(2)
    dz_root_hinge_rib = Input(0.2)
    dz_tip_hinge_rib = Input(0.2)
    rhl_root = Input(0.25)
    rhl_tip = Input(0.25)
    d_actuator = Input(0.125)
    ahl_tip = Input(0.75)
    d_front_spar = Input(0.07)
    d_back_spar = Input(0.025)
    pick_hingeribs = Input([1, 2, 3, 5, 6])

    #: Rudder size fraction. Rudder width/Fin root chord []
    #: :type: float
    rud_width_frac = Input(0.125)

    #: The height offset of the rudder from the bottom of the fin (height offset/first rib height) []
    #: :type: float
    rud_height_frac = Input(0.8)

    #: The fraction of the length of the rudder (rudder length/fin span) []
    #: :type: float
    rud_length_frac = Input(0.75)

    #: The fraction of the height of the actuator box from the bottom (box height/fin span)
    #: :type: float
    actuator_frac = Input(0.33)

    #: The fraction of the height of the first rib from the bottom (rib height/fin span) []
    #: :type: float
    rib0_frac = Input(0.0625)

    #: The fraction of the height of the ribs (rib height/fin span) []
    #: :type: float
    rib_frac = Input(0.125)

    #: Easy variable to offset all components along the x-axis [m]
    #: :type: float
    x_offset = Input(0)

    #: Easy variable to offset all components along the z-axis [m]
    #: :type: float
    z_offset = Input(0)

    @Attribute
    def d_hinge(self):
        """ Returns the distance from the trailing edge to the hinge plane [m]
        :rtype: float
        """
        return self.rud_width_frac * self.w_span

    @Attribute
    def r_rudder(self):
        """ Returns the distance from the bottom of the fin to the start of the rudder [m]
        :rtype: float
        """
        return self.rud_height_frac * self.p_zero

    @Attribute
    def b_rudder(self):
        """ Returns the length of the rudder [m]
        :rtype: float
        """
        return self.rud_length_frac * self.w_span

    @Attribute
    def r_actuator(self):
        """ Returns height of the actuator box from the bottom of the fin [m]
        :rtype: float
        """
        return self.actuator_frac / 8 * 2 * self.w_span

    @Attribute
    def p_zero(self):
        """ Returns the height of the first rib (from bottom) [m]
        :rtype: float
        """
        return  self.rib0_frac * self.w_span

    @Attribute
    def p_rib(self):
        """ Returns the height of the ribs (excluding the first one) [m]
        :rtype: float
        """
        return self.rib_frac * self.w_span

    @Attribute
    def calc_v_sweep_angle(self):
        """ Converts the input sweep angle (trailing edge) to 0.25 sweep angle for use in wing class [degrees]
        :rtype: float
        """
        if self.sweep_angle_user != 'NaN':
            if self.sweep_angle_user <= 8:
                # Conversion + user angle
                angle = atan(0.75 * (self.w_c_root - self.obj_vwing.w_c_tip) / self.w_span) + radians(self.sweep_angle_user)
            else:
                # check to prevent breaking the tool
                angle = atan(0.75 * (self.w_c_root - self.obj_vwing.w_c_tip) / self.w_span)
                warnings.warn("sweep angle too large, set to 0 degrees trailing edge")
        else:
            # Standard 'NaN' settings set the trailing edge sweep angle to 0 (vertical)
            angle = atan(0.75 * (self.w_c_root - self.obj_vwing.w_c_tip) / self.w_span)
        return degrees(angle)

    @Part(in_tree=False)
    # Create a wing object from the wing class
    def obj_vwing(self):
        return Wing(w_c_root=self.w_c_root,
                    w_span=self.w_span,
                    sweep_angle_user=self.calc_v_sweep_angle,
                    dihedral_angle_user=self.dihedral_angle_user,
                    TechFactor=self.TechFactor,
                    m_cruise=self.m_cruise,
                    taper_ratio_user=self.taper_ratio_user,
                    airfoil_tip=self.airfoil_tip,
                    airfoil_root=self.airfoil_root
                    )

    @Part(in_tree=False)
    def fin_shell(self):
        # Create a shell part from the wing solid faces
        return FusedShell(shape_in=self.obj_vwing.wing_part.faces[0],
                          tool=[self.obj_vwing.wing_part.faces[1], self.obj_vwing.wing_part.faces[2]],
                          label = 'Uncut Fin Shell')

    @Attribute(in_tree=False)
    def rudder_pln_locs(self):
        """ Converts the input sweep angle (trailing edge) to 0.25 sweep angle for use in wing class [degrees]
        :rtype: float
        """
        return [Point(self.w_c_root, 0, self.r_rudder), Point(self.w_c_root, 0, self.r_rudder + self.b_rudder)]

    @Part(in_tree=False)
    def hinge_pln(self):
        return Plane(reference=Point(self.w_c_root - self.d_hinge, 0, 0),
                     normal=Vector(1,
                                   0,
                                   0)
                     )

    @Part(in_tree=False)
    def rudder_plns(self):
        return Plane(quantify=2,
                     reference=self.rudder_pln_locs[child.index],
                     normal=Vector(0, 0, 1))

    @Part(in_tree = False)
    def rib_planes(self):
        return Plane(reference=Point(
            (((self.w_c_root - self.obj_vwing.w_c_tip) / (self.w_span)) * (self.p_zero + self.p_rib * child.index)), 0,
            self.p_zero + self.p_rib * child.index),
            normal=Vector(0,
                          0,
                          1),
            quantify=8,
            label = 'Rib Plane'
        )
    @Part(in_tree = True)
    def trans_rib_planes(self):
        return TranslatedPlane(built_from = self.rib_planes[child.index],
                               displacement=Vector(self.x_offset,0,self.z_offset),
                               quantify = len(self.rib_planes))

    @Part(in_tree=False)
    def fused_rudder_and_hinge_plns(self):
        return FusedShell(shape_in=self.fin_shell,
                          tool=[self.rudder_plns[0], self.rudder_plns[1], self.hinge_pln])

    @Part(in_tree=False)
    def rudder_plns_fused(self):
        return FusedShell(shape_in=self.fin_shell,
                          tool=self.rudder_plns)

    @Part
    def fixed_part(self):
        return FusedShell(shape_in=self.fused_rudder_and_hinge_plns.faces[16],
                          tool=[self.fused_rudder_and_hinge_plns.faces[0],
                                self.fused_rudder_and_hinge_plns.faces[1],
                                self.fused_rudder_and_hinge_plns.faces[2],
                                self.fused_rudder_and_hinge_plns.faces[5],
                                self.fused_rudder_and_hinge_plns.faces[6],
                                self.fused_rudder_and_hinge_plns.faces[7],
                                self.fused_rudder_and_hinge_plns.faces[8],
                                self.fused_rudder_and_hinge_plns.faces[9],
                                self.fused_rudder_and_hinge_plns.faces[10],
                                self.fused_rudder_and_hinge_plns.faces[11],
                                self.fused_rudder_and_hinge_plns.faces[13],
                                self.fused_rudder_and_hinge_plns.faces[14],
                                self.fused_rudder_and_hinge_plns.faces[17],
                                ],
                          transparency=0.6,
                          label = 'Fixed Fin')

    @Part(in_tree=False)
    def fixed_part_with_ribs(self):
        return FusedShell(shape_in=self.fixed_part,
                          tool=self.rib_planes)

    @Part(in_tree=False)
    def translate_rudder_closure_ribs_planes(self):
        return TranslatedPlane(built_from=self.rudder_plns[child.index],
                               displacement=Vector(0, 0, (1 - 2 * child.index) * 0.01),
                               quantify=2
                               )

    @Part(in_tree=False)
    def rudder_shell_partly(self):
        return FusedShell(shape_in=self.fused_rudder_and_hinge_plns.faces[3],
                          tool=[self.fused_rudder_and_hinge_plns.faces[4],
                                self.fused_rudder_and_hinge_plns.faces[14],
                                self.translate_rudder_closure_ribs_planes[0],
                                self.translate_rudder_closure_ribs_planes[1]
                                ]
                          )

    @Attribute(in_tree=True)
    def closure_ribs(self):
        collect = [self.rudder_shell_partly.faces[9], self.rudder_shell_partly.faces[10]]
        # Set names in the tree
        collect[0].label = 'Bottom'
        collect[1].label = 'Top'
        return collect


    @Part(in_tree=False)
    def rudder_shell(self):
        return FusedShell(shape_in=self.rudder_shell_partly.faces[3],
                          tool=[self.rudder_shell_partly.faces[4],
                                self.rudder_shell_partly.faces[5],
                                self.rudder_shell_partly.faces[9],
                                self.rudder_shell_partly.faces[10]
                                ]
                          )

    @Attribute(in_tree=False)
    def mac_def(self):
        sweep = radians(self.obj_vwing.sweep_angle)
        taper = self.obj_vwing.calculate_taper_ratio
        span = self.w_span
        cr = self.w_c_root

        z_loc = (2 * span / 6) * ((1 + 2 * taper) / (1 + taper))
        x_loc = z_loc / tan((0.5 * pi) - sweep)
        length = (2 * cr / 3) * ((1 + taper + taper ** 2) / (1 + taper))
        return [x_loc, z_loc, length]

    @Attribute(in_tree=False)
    def ref_area(self):
        return 0.5 * (self.w_c_root + self.obj_vwing.w_c_tip) * self.w_span

    @Attribute
    def hinge_locs(self):
        List = []
        number_hinges = len(self.pick_hingeribs)
        y_pos_root_begin = self.fixed_part_with_ribs.vertices[25 - 2 * self.pick_hingeribs[0]].point.y
        y_pos_root_end = self.fixed_part_with_ribs.vertices[24 - 2 * self.pick_hingeribs[0]].point.y
        y_pos_tip_begin = self.fixed_part_with_ribs.vertices[25 - 2 * self.pick_hingeribs[number_hinges - 1]].point.y
        y_pos_tip_end = self.fixed_part_with_ribs.vertices[24 - 2 * self.pick_hingeribs[number_hinges - 1]].point.y

        y_pos_root_begin_p = self.fixed_part_with_ribs.vertices[25 - 2 * self.pick_hingeribs[0]].point
        y_pos_root_end_p = self.fixed_part_with_ribs.vertices[24 - 2 * self.pick_hingeribs[0]].point
        y_pos_tip_begin_p = self.fixed_part_with_ribs.vertices[25 - 2 * self.pick_hingeribs[number_hinges - 1]].point
        y_pos_tip_end_p = self.fixed_part_with_ribs.vertices[24 - 2 * self.pick_hingeribs[number_hinges - 1]].point
        points_root = [y_pos_root_begin_p, y_pos_root_end_p]
        points_tip = [y_pos_tip_begin_p, y_pos_tip_end_p]
        root_distance = Point.distance(*points_root)
        tip_distance = Point.distance(*points_tip)

        # if self.pick_hingeribs[0] == 1 or 2:
        #     y_pos_root = self.fixed_part_with_ribs.vertices[4 + 5 * (self.pick_hingeribs[0] - 1)].point.y
        # else:
        #     y_pos_root = self.fixed_part_with_ribs.vertices[10].point.y
        #
        # if self.pick_hingeribs[number_hinges - 1] == 4 or 5:
        #     y_pos_tip = self.fixed_part_with_ribs.vertices[self.pick_hingeribs[number_hinges - 1] * 3].point.y
        # else:
        #     y_pos_tip = self.fixed_part_with_ribs.vertices[16].point.y

        z_pos_tip = self.p_zero + self.p_rib * (self.pick_hingeribs[number_hinges - 1] - 1)
        z_pos_root = self.p_zero + self.p_rib * (self.pick_hingeribs[0] - 1)

        for i in xrange(len(self.pick_hingeribs)):
            # Pointlist = Point(self.w_c_root - self.d_hinge,
            #                   y_pos_root - self.rhl_root + (
            #                       (-(y_pos_root - self.rhl_root) + (y_pos_tip - self.rhl_tip)) /
            #                       (x_pos_tip - x_pos_root)) * ((
            #                                                        self.p_zero + self.p_rib * (
            #                                                            self.pick_hingeribs[i] - 1)) - x_pos_root),
            #                   ((self.p_zero + self.p_rib * (self.pick_hingeribs[i] - 1))))
            PointList = Point(self.w_c_root - self.d_hinge,
                              y_pos_root_end + root_distance * self.rhl_root +
                              ((root_distance * self.rhl_root - tip_distance * self.rhl_tip) / (z_pos_root - z_pos_tip)) \
                              * (self.p_zero + self.p_rib * (self.pick_hingeribs[i] - 1) - z_pos_root),
                              self.p_zero + self.p_rib * (self.pick_hingeribs[i] - 1))
            List.append(PointList)
        return List
        # Pointlist = Point(self.w_c_root - self.d_hinge,
        #                   -root_distance * self.rhl_root - (
        #                       (-(root_distance) * self.rhl_root) + ((-tip_distance) * self.rhl_tip)) /
        #                   (x_pos_tip - x_pos_root)) * ((self.p_zero + self.p_rib * (
        #     self.pick_hingeribs[i] - 1)) - x_pos_root),
        # ((self.p_zero + self.p_rib * (self.pick_hingeribs[i] - 1))))
        # List.append(Pointlist)

    @Part(in_tree=False)
    def hingerib_plns(self):
        return Plane(quantify=len(self.hinge_locs),
                     reference=self.hinge_locs[child.index],
                     normal=Vector(0, 0, 1))

    @Part
    def hingerib_line(self):
        return LineSegment(self.hinge_locs[0],
                           self.hinge_locs[len(self.hinge_locs) - 1],
                           label = 'Rudder Hinge Line')

    @Part
    def actuator_planes(self):
        return Plane(quantify=2,
                     reference=Point(self.w_c_root - self.d_hinge,
                                     0,
                                     self.r_actuator + self.r_rudder + (self.d_actuator / 2) * (-1 + 2 * child.index)),
                     normal=Vector(0, 0, 1),
                     label = 'Actuator Rib Plane')

    @Part(in_tree=False)
    def formrib_plns(self):
        return Plane(quantify=(int(self.b_rudder / self.p_form_rib) - 1),
                     reference=Point(self.w_c_root - self.d_hinge,
                                     0,
                                     self.r_rudder + (self.p_form_rib * (child.index + 1)))
                     )

    @Attribute
    def actuator_hinge_locs(self):
        x_pos = self.w_c_root - self.d_hinge
        z_pos2 = self.r_actuator + self.r_rudder + (self.d_actuator / 2)
        z_pos1 = self.r_actuator + self.r_rudder - (self.d_actuator / 2)
        y_pos2 = ((self.rudder_shell.edges[5].point1.y + self.rudder_shell.edges[5].direction_vector.y / \
                   self.rudder_shell.edges[5].direction_vector.z * \
                   (self.rudder_shell.edges[5].point1.z - z_pos2)) - \
                  (self.rudder_shell.edges[7].point1.y + self.rudder_shell.edges[7].direction_vector.y / \
                   self.rudder_shell.edges[7].direction_vector.z * \
                   (self.rudder_shell.edges[7].point1.z - z_pos2))) * \
                 (1 - self.ahl_tip)
        begin_point = self.rudder_shell.edges[5].point1.y + self.rudder_shell.edges[5].direction_vector.y / \
                                                            self.rudder_shell.edges[5].direction_vector.z * \
                                                            (self.rudder_shell.edges[5].point1.z - z_pos2)
        end_point = (self.rudder_shell.edges[7].point1.y + self.rudder_shell.edges[7].direction_vector.y / \
                     self.rudder_shell.edges[7].direction_vector.z * \
                     (self.rudder_shell.edges[7].point1.z - z_pos2))
        begin_point = Point(0, begin_point, 0)
        end_point = Point(0, end_point, 0)
        points = [begin_point, end_point]
        distance = Point.distance(*points)
        y_pos2 = (self.rudder_shell.edges[5].point1.y + self.rudder_shell.edges[5].direction_vector.y / \
                  self.rudder_shell.edges[5].direction_vector.z * \
                  (self.rudder_shell.edges[5].point1.z - z_pos2)) + distance * self.ahl_tip

        y_pos1 = y_pos2 + self.hingerib_line.direction_vector.y / self.hingerib_line.direction_vector.z * \
                          (z_pos1 - z_pos2)

        return Point(x_pos, y_pos1, z_pos1), Point(x_pos, y_pos2, z_pos2)

    @Part
    def actuator_hinge_line(self):
        return LineSegment(self.actuator_hinge_locs[0],
                           self.actuator_hinge_locs[len(self.actuator_hinge_locs) - 1],
                           label = 'Actuator Hinge Line')

    @Part
    def actuator(self):
        return Box(0.1, 0.1, 0.2,
                   position=Position(location=Point(self.w_c_root - self.d_hinge - 0.25,
                                                    self.actuator_hinge_locs[0].y - 0.1 / 2,
                                                    self.r_actuator + self.r_rudder - 0.2 / 2),
                                     orientation=Orientation(x=Vector(1, 0, 0), y=Vector(0, 1, 0),
                                                             z=self.hingerib_line.direction_vector)),
                   label = 'Actuator Box')

    @Part
    def actuator_hinges(self):
        return Cylinder(0.02, 0.05,
                        position=translate(Position(location=self.actuator_hinge_locs[child.index],
                                                    orientation=Orientation(x=Vector(1, 0, 0), y=Vector(0, 1, 0),
                                                                            z=self.actuator_hinge_line.direction_vector)),
                                           'z', -0.05 / 2),
                        quantify=len(self.actuator_hinge_locs),
                        label = 'Actuator Hinge')

    @Part
    def hinges(self):
        return Cylinder(0.02, 0.05,
                        position=translate(Position(location=self.hinge_locs[child.index],
                                                    orientation=Orientation(x=Vector(1, 0, 0), y=Vector(0, 1, 0),
                                                                            z=self.hingerib_line.direction_vector)),
                                           'z', -0.05 / 2),
                        quantify=len(self.hinge_locs),
                        label = 'Rotation Hinge')

    @Attribute
    def curves(self):
        y_pos_root_begin = self.fixed_part_with_ribs.vertices[25 - 2 * self.pick_hingeribs[0]].point
        y_pos_root_end = self.fixed_part_with_ribs.vertices[24 - 2 * self.pick_hingeribs[0]].point
        points = [y_pos_root_begin, y_pos_root_end]
        distance = Point.distance(*points)

        z_hinge = self.p_zero + self.p_rib * (self.pick_hingeribs[0] - 1)
        z_bottom = self.rudder_shell.vertices[1].point.z
        y_bottom = points[1].y + distance * self.rhl_root + (
                                                                self.hingerib_line.direction_vector.y / self.hingerib_line.direction_vector.z) * (
                                                                z_bottom - z_hinge)
        z_up = self.rudder_shell.vertices[5].point.z
        y_up = y_bottom - (self.hingerib_line.direction_vector.y / self.hingerib_line.direction_vector.z) * (
            z_bottom - z_up)

        return [Arc(radius=y_bottom - self.rudder_shell.vertices[1].point.y,
                    angle=radians(90 + 32),
                    position=Position(location=Point(self.w_c_root - self.d_hinge,
                                                     y_bottom,
                                                     self.rudder_shell.vertices[1].point.z),
                                      orientation=Orientation(x=Vector(1, 0, 0),
                                                              y=Vector(0, 1, 0),
                                                              z=Vector(0, 0, -1))),
                    start=self.rudder_shell.vertices[1].point),
                Arc(radius=y_up - self.rudder_shell.vertices[4].point.y,
                    angle=radians(90 + 32),
                    position=Position(location=Point(self.w_c_root - self.d_hinge,
                                                     y_up,
                                                     self.rudder_shell.vertices[4].point.z),
                                      orientation=Orientation(x=Vector(1, 0, 0),
                                                              y=Vector(0, 1, 0),
                                                              z=Vector(0, 0, -1))),
                    start=self.rudder_shell.vertices[4].point),
                Arc(radius=self.rudder_shell.vertices[5].point.y - y_up,
                    angle=radians(90 + 32),
                    position=Position(location=Point(self.w_c_root - self.d_hinge,
                                                     y_up,
                                                     self.rudder_shell.vertices[5].point.z),
                                      orientation=Orientation(x=Vector(1, 0, 0),
                                                              y=Vector(0, 1, 0),
                                                              z=Vector(0, 0, 1))),
                    start=self.rudder_shell.vertices[5].point),
                Arc(radius=self.rudder_shell.vertices[2].point.y - y_bottom,
                    angle=radians(90 + 32),
                    position=Position(location=Point(self.w_c_root - self.d_hinge,
                                                     y_bottom,
                                                     self.rudder_shell.vertices[2].point.z),
                                      orientation=Orientation(x=Vector(1, 0, 0),
                                                              y=Vector(0, 1, 0),
                                                              z=Vector(0, 0, 1))),
                    start=self.rudder_shell.vertices[2].point)]

    @Part(in_tree=False)
    def curve_surface1(self):
        return MultiSectionSurface(profiles=[self.curves[0], self.curves[1]],
                                   path=self.rudder_shell.edges[5])

    @Part(in_tree=False)
    def curve_surface2(self):
        return MultiSectionSurface(profiles=[self.curves[2], self.curves[3]],
                                   path=self.rudder_shell.edges[7])

    @Part(in_tree=False)
    def pln_front_spar(self):
        return Plane(reference=Point(self.w_c_root - self.d_hinge + self.d_front_spar,
                                     0,
                                     0),
                     normal=Vector(1, 0, 0))

    @Part(in_tree=False)
    def pln_back_spar(self):
        return Plane(reference=Point(self.w_c_root - self.d_back_spar),
                     normal=Vector(1, 0, 0))

    @Part(in_tree=False)
    def fuse_back_spar(self):
        return FusedShell(shape_in=self.fin_shell,
                          tool=self.pln_back_spar)

    @Attribute
    def d_back_spar_warning(self):
        if (self.fuse_back_spar.edges[5].point1.y - self.fuse_back_spar.edges[6].point1.y) < 0.04:
            print 'warning d_back_spar = too small'
        return

    @Part(in_tree=False)
    def fused_spars(self):
        return FusedShell(shape_in=self.rudder_shell,
                          tool=[self.pln_back_spar, self.pln_front_spar])

    @Attribute
    def fused_le_skin_left(self):
        return FusedShell(shape_in=self.fused_spars.faces[4],
                          tool=[self.curve_surface1])

    @Attribute
    def fused_le_skin_right(self):
        return FusedShell(shape_in=self.fused_spars.faces[1],
                          tool=[self.curve_surface2])

    @Attribute
    def main_skin_left(self):
        return self.fused_spars.faces[12]

    @Attribute
    def main_skin_right(self):
        return self.fused_spars.faces[5]

    @Attribute
    def te_skin_left(self):
        return self.fused_spars.faces[9]

    @Attribute
    def te_skin_right(self):
        return self.fused_spars.faces[8]

    @Attribute(in_tree=True)
    def rudder_front_spar(self):
        spar = self.fused_spars.faces[13]
        spar.label = 'Front Spar'
        return spar

    @Attribute(in_tree=True)
    def rudder_back_spar(self):
        spar = self.fused_spars.faces[14]
        spar.label = 'Back Spar'
        return spar

    @Part(in_tree=False)
    def fuse_mainskin_ribs(self):
        return FusedShell(shape_in=self.main_skin_left,
                          tool=self.tool_creator)

    @Attribute
    def tool_creator(self):
        tool_list = [self.main_skin_right, self.rudder_front_spar, self.rudder_back_spar]
        for i in xrange(len(self.hingerib_plns)):
            tool_list.append(self.hingerib_plns[i])
        for i in xrange(len(self.actuator_planes)):
            tool_list.append(self.actuator_planes[i])
        for i in xrange(len(self.formrib_plns)):
            tool_list.append(self.formrib_plns[i])
        return tool_list

    @Attribute(in_tree=True)
    def rudder_ribs(self):
        list = []
        for i in xrange(len(self.fuse_mainskin_ribs.faces)):
            if self.fuse_mainskin_ribs.faces[i].uv_center_normal.z == 1:
                list.append(self.fuse_mainskin_ribs.faces[i])
        for x in xrange(0,len(list)):
            list[x].label='Rib'
        return list

    @Part(in_tree=True)
    def skins_rudder(self):
        return FusedShell(shape_in=self.te_skin_left,
                          tool=[self.main_skin_left, self.main_skin_right,
                                self.fused_le_skin_left, self.fused_le_skin_right,
                                self.te_skin_right],
                          transparency=0.6,
                          label = 'Rudder Skin')

    @Attribute
    def things_for_rotation(self):
        list = []
        list.append(self.skins_rudder)
        # for i in xrange(len(self.rudder_ribs)):
        #     list.append(self.rudder_ribs[i])

        return list

    @Part(in_tree=False)
    def turn_rudder(self):
        return RotatedShape(shape_in=self.things_for_rotation, rotation_point=self.hingerib_line.start,
                            vector=self.hingerib_line.direction_vector, angle=radians(30))




if __name__ == '__main__':
    from parapy.gui import display

    obj = VTailWing()
    display(obj)
