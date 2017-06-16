from math import *
import csv_handle as csvr
from parapy.geom import *
from wing import Wing
import warnings
from csv_in_out import *


# TODO:
# known bug, bij NaN taper ratio gaat hij kapot


class VTailWing(GeomBase):
    # This class creates a vertical wing including rudder

    # Label for the tree
    label = 'Tail Wing'

    # Create dicts
    constants = csvr.read_input("constants.csv")  # Fuselage Settings
    variables = csvr.read_input("vtail.csv")  # Fuselage Settings

    #: single wing span [m]
    #: :type: float
    w_span = Input()

    #: wing sweep angle [degrees]
    #: :type: float or str
    sweep_angle_user = Input(variables["sweep_angle_user"])  # Overwrites default function if ~= 'NaN'

    #: wing taper ratio []
    #: :type: float or str
    taper_ratio_user = Input(variables["taper_ratio_user"])  # Overwrites the default function if ~= 'NaN'

    #: wing dihedral angle [degrees]
    #: :type: float or str
    dihedral_angle_user = Input(variables["dihedral_angle_user"])  # Overwrites the default function if ~= 'NaN'

    #: jet cruise speed [mach]
    #: :type: float
    m_cruise = Input(constants["m_cruise"])  # Used to calculate the default sweep angle

    #: airfoil technology factor []
    #: :type: float
    TechFactor = Input(variables[
                           "TechFactor"])  # Technology factor is equal to 0.87 NACA 6 airfoil and 1 to other conventional airfoils

    #: the name of the root airfoil file
    #: :type: string
    airfoil_root = Input(variables["airfoil_root"])

    #: the name of the tip airfoil file
    #: :type: string
    airfoil_tip = Input(variables["airfoil_tip"])

    #: Distance in x direction of hinge plane with respect to the trailing edge[m]
    #: :type: float
    d_hinge_user = Input('NaN')  # Overwrites the default function if ~= 'NaN'

    #: Distance in z direction of fist fin rib with respect to the root[m]
    #: :type: float
    p_zero_user = Input('NaN')  # Overwrites the default function if ~= 'NaN'

    #: Distance in z direction of following fin ribs with respect to the previous one [m]
    #: :type: float
    p_rib_user = Input('NaN')  # Overwrites the default function if ~= 'NaN'

    #: Distance in z direction of the form rib with respect to the first form rib [m]
    #: :type: float
    p_form_rib_user = Input('NaN')  # Overwrites the default function if ~= 'NaN'

    #: Ratio of local width where the local hinge is located []
    #: :type: float
    rhl_root = Input(0.5)

    #: Ratio of local width where the local hinge is located []
    #: :type: float
    rhl_tip = Input(0.25)

    #: Ratio of local width where the local actuator hinge is located []
    #: :type: float
    ahl_tip = Input(0.25)

    #: Distance in z direction between the to actuator hinge planes [m]
    #: :type: float
    d_actuator = Input(0.125)

    #: Distance of front spar with respect to the hinge plane [m]
    #: :type: float
    d_front_spar = Input(0.07)

    #: Distance of back spar with respect to the trailing edge [m]
    #: :type: float
    d_back_spar = Input(0.025)

    #: Select which ribs are the hinge ribs. Default value is [1,2,3,4,5,6] al hinges are used. []
    #: :type: list of integers
    pick_hinge_ribs = Input([1, 2, 3, 4, 5, 6])

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
    #: If you want the actuator n ribs lower or higher just input 0.33 +/- p_rib*n
    #: :type: float
    actuator_frac = Input(0.33)

    #: The fraction of the height of the first rib from the bottom (rib height/fin span) []
    #: :type: float
    rib0_frac = Input(0.0625)

    #: The fraction of the height of the ribs (rib height/fin span) []
    #: :type: float
    rib_frac = Input(0.125)

    #: The fraction of the height of the form ribs (form rib height/fin span) []
    #: :type: float
    form_rib_frac = Input(0.075)

    #: Easy variable to offset all components along the x-axis [m]
    #: :type: float
    x_offset = Input(0)

    #: Easy variable to offset all components along the z-axis [m]
    #: :type: float
    z_offset = Input(0)

    #: Fraction to determine root chord size in relation to the span length
    #: :type: float
    root_frac = Input(variables["root_frac"])

    #: The angle at which the rudder is rotated [degrees]
    #: :type: float
    rud_angle = Input(variables["rud_angle"])

    @Input
    def w_c_root(self):
        """
        Calculates the root chord length
        :rtype: float
        """
        return self.root_frac * self.w_span

    @Attribute
    def d_hinge(self):
        """ Returns the distance from the trailing edge to the hinge plane [m]
        :rtype: float
        """
        if self.d_hinge_user == 'NaN':  # if not defined, use default formula
            distance = self.rud_width_frac * self.w_span
        else:
            distance = self.d_hinge_user
        return distance

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
        return self.actuator_frac * self.w_span

    @Attribute
    def p_zero(self):
        """ Returns the height of the first rib (from bottom) [m]
        :rtype: float
        """
        if self.p_zero_user == 'NaN':  # if not defined, use default formula
            distance = self.rib0_frac * self.w_span
        else:
            distance = self.p_zero_user
        return distance

    @Attribute
    def p_rib(self):
        """ Returns the height of the ribs (excluding the first one) [m]
        :rtype: float
        """
        if self.p_rib_user == 'NaN':  # if not defined, use default formula
            distance = self.rib_frac * self.w_span
        else:
            distance = self.p_rib_user
        return distance

    @Attribute
    def p_form_rib(self):
        """ Returns the height of the form ribs (excluding the first one) [m]
        :rtype: float
        """
        if self.p_form_rib_user == 'NaN':  # if not defined, use default formula
            distance = self.form_rib_frac * self.w_span
        else:
            distance = self.p_form_rib_user
        return distance

    @Attribute
    def calc_v_sweep_angle(self):
        """ Converts the input sweep angle (trailing edge) to 0.25 sweep angle for use in wing class [degrees]
        :rtype: float
        """
        if self.sweep_angle_user != 'NaN':
            if self.sweep_angle_user <= 8:
                # Conversion + user angle
                angle = atan(0.75 * (self.w_c_root - self.obj_vwing.w_c_tip) / self.w_span) \
                        + radians(self.sweep_angle_user)
            else:
                # check to prevent breaking the tool
                angle = atan(0.75 * (self.w_c_root - self.obj_vwing.w_c_tip) / self.w_span)
                warnings.warn("sweep angle too large, set to 0 degrees trailing edge")
        else:
            # Standard 'NaN' settings set the trailing edge sweep angle to 0 (vertical)
            angle = atan(0.75 * (self.w_c_root - self.obj_vwing.w_c_tip) / self.w_span)
        return degrees(angle)

    @Part(in_tree=False)
    def obj_vwing(self):
        """ Create a wing object from the wing class
        :rtype: part
        """
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
    def trans_vwing(self):
        """
        Translate the wing solid to its correct position using the offsets
        :rtype: TranslatedShape
        """
        return TranslatedShape(shape_in=self.obj_vwing.wing_part,
                               displacement=Vector(self.x_offset, 0, self.z_offset))

    @Attribute(in_tree=False)
    def rudder_pln_locs(self):
        """ determines the location of the rudder plane
        :rtype: float
        """
        return [Point(self.w_c_root + self.x_offset, 0, self.r_rudder + self.z_offset),
                Point(self.w_c_root + self.x_offset, 0, self.r_rudder + self.b_rudder + self.z_offset)]

    @Part(in_tree=False)
    def hinge_pln(self):
        """ Creates a plane at a distance of d_hinge from the TE
        :rtype: part
        """
        return Plane(
            reference=Point(self.w_c_root - self.d_hinge + self.x_offset,  # point at d_hinge from TE in x direction
                            0,
                            self.z_offset),
            normal=Vector(1, 0, 0)  # normal vector of the plane in x direction
            )

    @Part(in_tree=False)
    def rudder_separation_plns(self):
        """ Creates planes at the locations defined in rudder_separation_pln_locs
        :rtype: part
        """
        return Plane(quantify=2,
                     reference=self.rudder_pln_locs[child.index],  # locations of the rudder separation planes
                     normal=Vector(0, 0, 1))  # normal vector of the plane in z direction

    @Part(in_tree=True)
    def rib_planes(self):
        """ Creates planes with the origin in the LE and with a normal in z direction
        :rtype: part
        """
        return Plane(
            reference=Point((((self.w_c_root - self.obj_vwing.w_c_tip) /  # Make sure that the origin of the plane...
                              (self.w_span)) * (self.p_zero + self.p_rib * child.index) + self.x_offset),
                            # follows the LE
                            0,
                            self.p_zero + self.p_rib * child.index + self.z_offset),
            normal=Vector(0, 0, 1),  # normal vector of the plane in z direction
            quantify=8,
            label='Rib Plane'
        )

    @Part(in_tree=False)
    def fused_rudder_and_hinge_plns(self):
        """ Fusion of fin_shell and rudder separation planes and hinges plane to cut out the rudder
        :rtype: part
        """
        return FusedShell(shape_in=self.trans_vwing.shells[0],
                          tool=[self.rudder_separation_plns[0],
                                self.rudder_separation_plns[1],
                                self.hinge_pln])

    @Part(in_tree=False)
    def fixed_part(self):
        """ Combine faces to make a fixed part without the rudder
        :rtype: part
        """
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
                                self.fused_rudder_and_hinge_plns.faces[17],
                                ],
                          transparency=0.6,
                          label='Fixed Fin',
                          color='red')

    @Part(in_tree=False)
    def fixed_part_with_ribs(self):
        """" Fusion of fixed_part shell with the rib_planes to use it later in calculation
        for choosing hingeribs and determination of position
        """
        return FusedShell(shape_in=self.fixed_part,
                          tool=self.rib_planes)

    @Part(in_tree=False)
    def translate_rudder_closure_ribs_planes(self):
        """ Translate closure ribs of the rudder to make sure it doesn't interfere with the fixed part
        """
        return TranslatedPlane(built_from=self.rudder_separation_plns[child.index],
                               displacement=Vector(0, 0, (1 - 2 * child.index) * 0.01),
                               quantify=2
                               )

    @Part(in_tree=False)
    def rudder_shell_partly(self):
        """Fusion of the rudder planes with the closure ribs"""
        return FusedShell(shape_in=self.fused_rudder_and_hinge_plns.faces[3],
                          tool=[self.fused_rudder_and_hinge_plns.faces[4],
                                self.fused_rudder_and_hinge_plns.faces[14],
                                self.translate_rudder_closure_ribs_planes[0],
                                self.translate_rudder_closure_ribs_planes[1]
                                ]
                          )

    @Attribute(in_tree=False)
    def closure_ribs(self):
        """ Define closure_ribs
        :rtype: tuple
        """
        collect = [self.rudder_shell_partly.faces[9], self.rudder_shell_partly.faces[10]]
        # Set names in the tree
        collect[0].label = 'Bottom'
        collect[1].label = 'Top'
        return collect

    @Part(in_tree=False)
    def rudder_shell(self):
        """ Fusion of the first basic rudder
        :rtype: part
        """
        return FusedShell(shape_in=self.rudder_shell_partly.faces[3],
                          tool=[self.rudder_shell_partly.faces[4],
                                self.rudder_shell_partly.faces[5],
                                self.rudder_shell_partly.faces[9],
                                self.rudder_shell_partly.faces[10]
                                ]
                          )

    @Attribute(in_tree=False)
    def mac_def(self):
        """ Defines x location, z location and length of the mean aerodynamic chord
        :rtype: tuple
        """
        sweep = radians(self.obj_vwing.sweep_angle)  # sweep of vtailwing
        taper = self.obj_vwing.taper_ratio  # taper of vtailwing
        span = self.w_span  # span of vtailwing
        cr = self.w_c_root  # root chord of vtailwing

        z_loc = (2 * span / 6) * ((1 + 2 * taper) / (1 + taper))  # calculate z location
        x_loc = z_loc / tan((0.5 * pi) - sweep)  # calculate x location
        length = (2 * cr / 3) * ((1 + taper + taper ** 2) / (1 + taper))  # calculate length
        return [x_loc, z_loc, length]

    @Attribute(in_tree=False)
    def ref_area(self):
        return 0.5 * (self.w_c_root + self.obj_vwing.w_c_tip) * self.w_span

    @Attribute
    def hinge_locs(self):
        """ Define location of the hinges in x,y,z direction
        :rtype: list
        """
        # initialize
        List = []
        number_hinges = len(self.pick_hinge_ribs)
        # Define position of intersection of ribs and egdes.
        y_pos_root_begin_p = self.fixed_part_with_ribs.vertices[25 - 2 * self.pick_hinge_ribs[0]].point
        y_pos_root_end_p = self.fixed_part_with_ribs.vertices[24 - 2 * self.pick_hinge_ribs[0]].point
        y_pos_tip_begin_p = self.fixed_part_with_ribs.vertices[25 - 2 * self.pick_hinge_ribs[number_hinges - 1]].point
        y_pos_tip_end_p = self.fixed_part_with_ribs.vertices[24 - 2 * self.pick_hinge_ribs[number_hinges - 1]].point

        # Define distance
        points_root = [y_pos_root_begin_p, y_pos_root_end_p]
        points_tip = [y_pos_tip_begin_p, y_pos_tip_end_p]
        root_distance = Point.distance(*points_root)
        tip_distance = Point.distance(*points_tip)

        # Define z position
        z_pos_tip = self.p_zero + self.p_rib * (self.pick_hinge_ribs[number_hinges - 1] - 1) + self.z_offset
        z_pos_root = self.p_zero + self.p_rib * (self.pick_hinge_ribs[0] - 1) + self.z_offset

        # Append hingeloc points
        for i in xrange(len(self.pick_hinge_ribs)):
            PointList = Point(self.w_c_root - self.d_hinge + self.x_offset,
                              y_pos_root_end_p.y - root_distance * self.rhl_root +
                              (((y_pos_root_end_p.y - root_distance * self.rhl_root) - (
                              y_pos_tip_end_p.y - tip_distance * self.rhl_tip)) / (z_pos_root - z_pos_tip)) \
                              * (self.z_offset + self.p_zero + self.p_rib * (self.pick_hinge_ribs[i] - 1) - z_pos_root),
                              self.p_zero + self.p_rib * (self.pick_hinge_ribs[i] - 1) + self.z_offset)
            List.append(PointList)
        return List

    @Part(in_tree=False)
    def hingerib_plns(self):
        return Plane(quantify=len(self.hinge_locs),
                     reference=self.hinge_locs[child.index],
                     normal=Vector(0, 0, 1))

    @Part
    def hingerib_line(self):
        return LineSegment(self.hinge_locs[0],
                           self.hinge_locs[len(self.hinge_locs) - 1],
                           label='Rudder Hinge Line')

    @Part
    def actuator_planes(self):
        return Plane(quantify=2,
                     reference=Point(self.w_c_root - self.d_hinge + self.x_offset,
                                     0,
                                     self.r_actuator + self.r_rudder + (self.d_actuator / 2) * (
                                     -1 + 2 * child.index) + self.z_offset),
                     normal=Vector(0, 0, 1),
                     label='Actuator Rib Plane')

    @Part(in_tree=False)
    def formrib_plns(self):
        return Plane(quantify=(int(self.b_rudder / self.p_form_rib) - 1),
                     reference=Point(self.w_c_root - self.d_hinge + self.x_offset,
                                     0,
                                     self.r_rudder + (self.p_form_rib * (child.index + 1)) + self.z_offset)
                     )

    @Attribute
    def actuator_hinge_locs(self):
        """ Define location of the actuator hinges in x,y,z direction
        :rtype: list
        """
        x_pos = self.w_c_root - self.d_hinge  # define x posistion

        z_pos2 = self.r_actuator + self.r_rudder + (self.d_actuator / 2)  # define z position upper point
        z_pos1 = self.r_actuator + self.r_rudder - (self.d_actuator / 2)  # define z position lower point

        # define distance of intersection points with the edges on z location of upperpoint
        begin_point_y = self.rudder_shell.edges[7].point1.y - self.rudder_shell.edges[7].direction_vector.y / \
                                                              self.rudder_shell.edges[7].direction_vector.z * \
                                                              (self.rudder_shell.edges[7].point1.z - z_pos2)
        end_point_y = (self.rudder_shell.edges[3].point1.y - self.rudder_shell.edges[3].direction_vector.y /
                       self.rudder_shell.edges[3].direction_vector.z *
                       (self.rudder_shell.edges[3].point1.z - z_pos2))
        begin_point = Point(0, begin_point_y, 0)
        end_point = Point(0, end_point_y, 0)
        points = [begin_point, end_point]
        distance = Point.distance(*points)

        y_pos2 = begin_point_y + distance * self.ahl_tip  # define y position
        y_pos1 = y_pos2 + self.hingerib_line.direction_vector.y / self.hingerib_line.direction_vector.z * \
                          (z_pos1 - z_pos2)

        return Point(x_pos + self.x_offset, y_pos1, z_pos1 + self.z_offset), Point(x_pos + self.x_offset, y_pos2,
                                                                                   z_pos2 + self.z_offset)

    @Part(in_tree=False)
    def actuator_hinge_line(self):
        return LineSegment(self.actuator_hinge_locs[0],
                           self.actuator_hinge_locs[len(self.actuator_hinge_locs) - 1],
                           label='Actuator Hinge Line')

    @Part
    def actuator(self):
        return Box(0.1, 0.1, 0.2,
                   position=Position(location=Point(self.w_c_root - self.d_hinge - 0.25 + self.x_offset,
                                                    self.actuator_hinge_locs[0].y - 0.1 / 2,
                                                    self.r_actuator + self.r_rudder - 0.2 / 2 + self.z_offset),
                                     orientation=Orientation(x=Vector(1, 0, 0), y=Vector(0, 1, 0),
                                                             z=self.hingerib_line.direction_vector)),
                   label='Actuator Box')

    @Part(in_tree=False)
    def actuator_hinges(self):
        return Cylinder(0.02, 0.05,
                        position=translate(Position(location=self.actuator_hinge_locs[child.index],
                                                    orientation=Orientation(x=Vector(1, 0, 0), y=Vector(0, 1, 0),
                                                                            z=self.actuator_hinge_line.direction_vector)),
                                           'z', -0.05 / 2),
                        quantify=len(self.actuator_hinge_locs),
                        label='Actuator Hinge')

    @Part
    def hinges(self):
        return Cylinder(0.02, 0.05,
                        position=translate(Position(location=self.hinge_locs[child.index],
                                                    orientation=Orientation(x=Vector(1, 0, 0), y=Vector(0, 1, 0),
                                                                            z=self.hingerib_line.direction_vector)),
                                           'z', -0.05 / 2),
                        quantify=len(self.hinge_locs),
                        label='Rotation Hinge')

    @Attribute
    def curves(self):
        x_pos = self.w_c_root - self.d_hinge + self.x_offset

        pos_root_begin = self.rudder_shell.vertices[0].point
        pos_root_end = self.rudder_shell.vertices[2].point
        pos_tip_begin = self.rudder_shell.vertices[3].point
        pos_tip_end = self.rudder_shell.vertices[5].point

        y_pos_hingeline_root = self.hingerib_line.point1.y - (self.hingerib_line.direction_vector.y /
                                                              self.hingerib_line.direction_vector.z) * \
                                                             (pos_root_begin.z - self.hingerib_line.point1.z)
        y_pos_hingeline_tip = self.hingerib_line.point2.y - (self.hingerib_line.direction_vector.y /
                                                             self.hingerib_line.direction_vector.z) * \
                                                            (pos_tip_begin.z - self.hingerib_line.point2.z)

        point_origin_circ_root = Point(x_pos, y_pos_hingeline_root, pos_root_begin.z)
        point_origin_circ_tip = Point(x_pos, y_pos_hingeline_tip, pos_tip_begin.z)

        root_begin = (point_origin_circ_root, pos_root_begin)
        root_end = (point_origin_circ_root, pos_root_end)
        tip_begin = (point_origin_circ_tip, pos_tip_begin)
        tip_end = (point_origin_circ_tip, pos_tip_end)

        radius_root_begin = Point.distance(*root_begin)
        radius_root_end = Point.distance(*root_end)
        radius_tip_begin = Point.distance(*tip_begin)
        radius_tip_end = Point.distance(*tip_end)

        return [Arc(radius=radius_root_begin,
                    angle=radians(90 + self.rud_angle),
                    position=Position(location=point_origin_circ_root,
                                      orientation=Orientation(x=Vector(1, 0, 0),
                                                              y=Vector(0, 1, 0),
                                                              z=Vector(0, 0, 1))),
                    start=pos_root_begin),
                Arc(radius=radius_root_end,
                    angle=radians(90 + self.rud_angle),
                    position=Position(location=point_origin_circ_root,
                                      orientation=Orientation(x=Vector(1, 0, 0),
                                                              y=Vector(0, 1, 0),
                                                              z=Vector(0, 0, -1))),
                    start=pos_root_end),
                Arc(radius=radius_tip_begin,
                    angle=radians(90 + self.rud_angle),
                    position=Position(location=point_origin_circ_tip,
                                      orientation=Orientation(x=Vector(1, 0, 0),
                                                              y=Vector(0, 1, 0),
                                                              z=Vector(0, 0, 1))),
                    start=pos_tip_begin),
                Arc(radius=radius_tip_end,
                    angle=radians(90 + self.rud_angle),
                    position=Position(location=point_origin_circ_tip,
                                      orientation=Orientation(x=Vector(1, 0, 0),
                                                              y=Vector(0, 1, 0),
                                                              z=Vector(0, 0, -1))),
                    start=pos_tip_end)]

    @Part(in_tree=False)
    def curve_surface1(self):
        return MultiSectionSurface(profiles=[self.crv[0], self.crv[2]],
                                   path=self.rudder_shell.edges[3])

    @Part(in_tree=False)
    def curve_surface2(self):
        return MultiSectionSurface(profiles=[self.crv[1], self.crv[3]],
                                   path=self.rudder_shell.edges[7])

    @Part(in_tree=False)
    def pln_front_spar(self):
        return Plane(reference=Point(self.w_c_root - self.d_hinge + self.d_front_spar + self.x_offset,
                                     0,
                                     self.z_offset),
                     normal=Vector(1, 0, 0))

    @Part(in_tree=False)
    def pln_back_spar(self):
        return Plane(reference=Point(self.w_c_root - self.d_back_spar + self.x_offset,
                                     0,
                                     self.z_offset),
                     normal=Vector(1, 0, 0))

    @Part(in_tree=False)
    def fused_spars(self):
        return FusedShell(shape_in=self.rudder_shell,
                          tool=[self.pln_back_spar, self.pln_front_spar])

    @Attribute
    def crv(self):
        start= self.fused_spars.faces[1].vertices[1].point
        end = self.fused_spars.faces[1].vertices[0].point
        crv1 = LineSegment(start=start, end=end)
        crv2 = self.curves[0]
        obj1 = ComposedCurve(built_from=[crv1, crv2])

        start= self.fused_spars.faces[4].vertices[0].point
        end = self.fused_spars.faces[4].vertices[1].point
        crv1 = LineSegment(start=start, end=end)
        crv2 = self.curves[1]
        obj2 = ComposedCurve(built_from=[crv1, crv2])

        start= self.fused_spars.faces[1].vertices[2].point
        end = self.fused_spars.faces[1].vertices[3].point
        crv1 = LineSegment(start=start, end=end)
        crv2 = self.curves[2]
        obj3 = ComposedCurve(built_from=[crv1, crv2])

        start= self.fused_spars.faces[4].vertices[3].point
        end = self.fused_spars.faces[4].vertices[2].point
        crv1 = LineSegment(start=start, end=end)
        crv2 = self.curves[3]
        obj4 = ComposedCurve(built_from=[crv1, crv2])
        return obj1,obj2,obj3,obj4

    @Attribute
    def fused_le_skin_left(self):
        return self.curve_surface1

    @Attribute
    def fused_le_skin_right(self):
        return self.curve_surface2

    @Attribute
    def main_skin_left(self):
        return self.fused_spars.faces[8]

    @Attribute
    def main_skin_right(self):
        return self.fused_spars.faces[5]

    @Attribute
    def te_skin_left(self):
        return self.fused_spars.faces[9]

    @Attribute
    def te_skin_right(self):
        return self.fused_spars.faces[11]

    @Attribute(in_tree=False)
    def rudder_front_spar(self):
        spar = self.fused_spars.faces[13]
        spar.label = 'Front Spar'
        return spar

    @Attribute(in_tree=False)
    def rudder_back_spar(self):
        """ Collects the rudder back spar face
        :rtype: list
        """
        if Point.distance(self.fused_spars.faces[14].vertices[1].point,
                          self.fused_spars.faces[14].vertices[2].point) < 0.04:
            warnings.showwarning(message='d_back_spar = too small', category=UserWarning, filename='vtailwing',
                                 lineno=735)

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

    @Attribute(in_tree=False)
    def rudder_ribs(self):
        """ List all planes with its normal in z direction
        :rtype: list
        """
        list = []
        for i in xrange(len(self.fuse_mainskin_ribs.faces)):
            if self.fuse_mainskin_ribs.faces[i].uv_center_normal.z == 1:
                list.append(self.fuse_mainskin_ribs.faces[i])
        for x in xrange(0, len(list)):
            list[x].label = 'Rib'
        return list

    @Part(in_tree=True)
    def skins_rudder(self):
        """ Fuses all rudder skins
        :rtype: part
        """
        return FusedShell(shape_in=self.main_skin_left,
                          tool=[self.main_skin_right,
                                self.fused_le_skin_left, self.fused_le_skin_right,
                                self.te_skin_right, self.te_skin_left],
                          transparency=0.6,
                          label='Rudder Skin')

    @Attribute
    def things_for_rotation(self):
        """ Gives a list of all the faces/skins/shells that needs to be turned
        :rtype: list
        """
        list = []
        list.append(self.skins_rudder.shells[0])
        for i in xrange(len(self.rudder_ribs)):
            list.append(self.rudder_ribs[i].faces[0])
        list.append(self.rudder_back_spar)
        list.append(self.rudder_front_spar)
        for i in xrange(len(self.actuator_hinges)):
            list.append(self.actuator_hinges[i].solids[0])
        for i in xrange(len(self.closure_ribs)):
            list.append(self.closure_ribs[i].faces[0])
        list.append(self.actuator_hinge_line)
        return list

    @Attribute
    def transparency_definer(self):
        """ Gives a list of 0.6 and multiple zeros to define the transparency of the rudderskin
        :rtype: list
        """
        list = []
        list.append(0.6)
        for i in xrange(len(self.things_for_rotation) - 1):
            list.append(0)
        return list

    @Attribute
    def label_definer(self):
        """ Gives a list of names
        :rtype: list
        """
        list = ['Rudder Shell', 'Hinge Rib', 'Form Rib', 'Hinge Rib', 'Form Rib',
                'Form Rib', 'Hinge Rib', 'Form Rib', 'Actuator Hinge Rib',
                'Actuator Hinge Rib', 'Form Rib', 'Hinge Rib', 'Form Rib',
                'Hinge Rib', 'Form Rib', 'Form Rib', 'Hinge Rib', 'Form Rib',
                'Back Spar', 'Front Spar', 'Actuator Hinge', 'Actuator Hinge',
                'Closure Rib', 'Closure Rib', 'Actuator Hinge Line']
        return list

    @Part(in_tree=True)
    def turned_rudder(self):
        """ Turns all defined faces/skins/shells in things_for_rotation
        :rtype: part
        """
        return RotatedShape(shape_in=self.things_for_rotation[child.index], rotation_point=self.hingerib_line.start,
                            vector=self.hingerib_line.direction_vector, angle=radians(self.rud_angle),
                            quantify=len(self.things_for_rotation), transparency=self.transparency_definer[child.index],
                            label=self.label_definer[child.index])

    @Attribute
    def save_vars(self):
        """ Saves the variables of current settings to an output file

        :rtype: string and csv
        """
        path = csvr.generate_path("vtail.csv")
        first_row = True
        with open(path[0], 'rb') as file:  # Open file
            reader = csv.reader(file, delimiter=',', quotechar='|')  # Read into reader and section rows and columns
            with open(path[1], 'wb') as outfile:
                filewriter = csv.writer(outfile, delimiter=',', quotechar='|')  # Create the writer
                for row in reader:  # Go over the rows in the file
                    if first_row == True:  # Skip the first row
                        filewriter.writerow(row)
                        first_row = False
                    else:
                        # Find the name of the variable that we want to request and save
                        var_name = row[0]

                        value = getattr(self, var_name)
                        # Update the value in row
                        row[1] = value
                        # Write the row to a new file
                        filewriter.writerow(row)
        return 'Saved'


if __name__ == '__main__':
    from parapy.gui import display

    obj = VTailWing()
    display(obj)
