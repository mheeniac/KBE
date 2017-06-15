from parapy.exchange import STEPWriter

from fuselage import Fuselage
from wingset import *
from vtailwing import *
from bay_analysis_tool.bay_analysis import BayAnalysis
from csv_read import *
from avl import *
from material_allocation import *
from shear_bend import *

# TODO:

# Read function from external file to read the .csv files
fuse = csvr.read_input("fuselage.csv")  # Fuselage Settings
const = csvr.read_input("constants.csv")  # constants Settings
mwing = csvr.read_input("mwing.csv")  # Main wing Settings
vtail = csvr.read_input("vtail.csv")  # Vertical tail settings
htail = csvr.read_input("htail.csv")  # Vertical tail settings


class Aircraft(GeomBase):
    # Name for the root object in the tree
    label = 'Business Jet'

    # -------------------
    ## FUSELAGE VARIABLES
    # -------------------

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

    # --------------------
    ## MAIN WING VARIABLES
    # --------------------

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
    TechFactor = Input(
        mwing["TechFactor"])  # Technology factor is equal to 0.87 NACA 6 airfoil and 1 to other conventional airfoils

    #: the name of the root airfoil file
    #: :type: string
    airfoil_root = Input(mwing["airfoil_root"])

    #: the name of the tip airfoil file
    #: :type: string
    airfoil_tip = Input(mwing["airfoil_tip"])

    #: Percentile location of the main wing aerodynamic center of the cabin length
    #: :type: float
    w_loc_perc = Input(const["w_loc_perc"])

    # ----------------
    ## VTAIL VARIABLES
    # ----------------
    #: The angle at which the rudder is rotated [degrees]
    #: :type: float
    rud_angle = Input(vtail["rud_angle"])

    #: The desired distance between the vertical tail aerodynamic centre and the main wing aerodynamic centre
    #: :type: float
    l_v = Input(6.)

    #: Fraction to determine root chord size in relation to the span length
    #: :type: float
    root_frac = Input(vtail["root_frac"])

    #: Tail volume coefficient
    #: :type: float
    Vv = Input(const["Vv"])

    #: wing sweep angle [degrees]
    #: :type: float or str
    vert_sweep_angle_user = Input(vtail["sweep_angle_user"])  # Overwrites default function if ~= 'NaN'

    #: wing taper ratio []
    #: :type: float or str
    vert_taper_ratio_user = Input(vtail["taper_ratio_user"])  # Overwrites the default function if ~= 'NaN'

    #: wing dihedral angle [degrees]
    #: :type: float or str
    vert_dihedral_angle_user = Input(vtail["dihedral_angle_user"])  # Overwrites the default function if ~= 'NaN'

    #: airfoil technology factor []
    #: :type: float
    vert_TechFactor = Input(vtail[
                                "TechFactor"])  # Technology factor is equal to 0.87 NACA 6 airfoil and 1 to other conventional airfoils

    #: the name of the root airfoil file
    #: :type: string
    vert_airfoil_root = Input(vtail["airfoil_root"])

    #: the name of the tip airfoil file
    #: :type: string
    vert_airfoil_tip = Input(vtail["airfoil_tip"])

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
    rhl_root = Input(0.25)

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
    pick_hinge_ribs = Input([2, 4, 5, 6])

    #: Rudder size fraction. Rudder width/Fin root chord []
    #: :type: float
    rud_width_frac = Input(0.2)

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

    #: Iteration size of to make the shear and bend moment lines [m]
    #: :type: float
    dx = Input(0.001)

    # -----------------
    ## HTail variables
    # ----------------

    #: wing sweep angle [degrees]
    #: :type: float or str
    hor_sweep_angle_user = Input(htail["sweep_angle"])  # Overwrites default function if ~= 'NaN'

    #: wing taper ratio []
    #: :type: float or str
    hor_taper_ratio_user = Input(htail["taper_ratio"])  # Overwrites the default function if ~= 'NaN'

    #: wing dihedral angle [degrees]
    #: :type: float or str
    hor_dihedral_angle_user = Input(htail["dihedral_angle"])  # Overwrites the default function if ~= 'NaN'

    #: airfoil technology factor []
    #: :type: float
    hor_TechFactor = Input(htail[
                               "TechFactor"])  # Technology factor is equal to 0.87 NACA 6 airfoil and 1 to other conventional airfoils

    #: the name of the root airfoil file
    #: :type: string
    hor_airfoil_root = Input(htail["airfoil_root"])

    #: the name of the tip airfoil file
    #: :type: string
    hor_airfoil_tip = Input(htail["airfoil_tip"])

    #: Span of a single horizontal tail wing [m]
    #: :type: float
    hor_w_span = Input(htail["w_span"])

    #: Root chord length [m]
    #: :type: float
    h_w_c_root = Input(htail["w_c_root"])

    # -------------
    ## Constants
    # -------------

    #: The air density at flight altitude [kg/m^3]
    #: :type: float
    rho = Input(const["rho"])

    #: Factor of safety for the AVL calculations
    #: :type: float
    FoS = Input(const["FoS"])

    # Rudder force width offset fraction of total rudder width (float)
    #: :type: float
    x_fc = Input(const["x_fc"])

    @Part
    def fuselage_part(self):
        # Create a part from the fuselage class
        return Fuselage(cabin_diameter=self.cabin_diameter,
                        cabin_length=self.cabin_length,
                        nose_slenderness=self.nose_slenderness,
                        tail_slenderness=self.tail_slenderness,
                        upsweep_angle=self.upsweep_angle,
                        tail_taper=self.tail_taper,
                        n_section=self.n_section
                        )

    # -----------------------
    ## This is the main wing
    # -----------------------
    @Part(in_tree=False)
    def obj_main_wing(self):
        # Create a wing object for the main wings of the plane from the wingset class
        return Wingset(w_c_root=self.w_c_root,
                       sweep_angle=self.sweep_angle,
                       taper_ratio=self.taper_ratio,
                       dihedral_angle=self.dihedral_angle,
                       m_cruise=self.m_cruise,
                       TechFactor=self.TechFactor,
                       w_span=self.w_span,
                       airfoil_root=self.airfoil_root,
                       airfoil_tip=self.airfoil_tip,
                       save_name='mwing.csv')

    @Part(in_tree=False)
    def rotate_main_wing(self):
        # Rotate the wing solids so that it is aligned with the fuselage
        return RotatedShape(shape_in=self.obj_main_wing.wingset[child.index],
                            rotation_point=Point(0, 0, 0),
                            vector=Vector(1, 0, 0),
                            angle=radians(90),
                            quantify=2
                            )

    @Part(in_tree=True)
    def main_wing(self):
        # Translate the wings such that the aerodynamic center is at 60% of the cabin length
        return TranslatedShape(shape_in=self.rotate_main_wing[child.index],
                               displacement=Vector(
                                   self.adc_diff,  # Translate along fuselage length with calculated difference
                                   0,
                                   self.obj_main_wing.calc_lowest_point+0.01),  # Translate down so that it is bottom wing
                               quantify=2,
                               color='red',
                               label=['Left Wing', 'Right Wing'][child.index]
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
        return LineSegment(start=Point(0.25 * self.w_c_root + self.obj_main_wing.mac_def[0] -
                                       0.25 * self.obj_main_wing.mac_def[2],
                                       0,
                                       0),
                           end=Point(0.25 * self.w_c_root + self.obj_main_wing.mac_def[0] +
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
                               line_thickness=6,
                               label='Main Wing MAC')

    @Part
    def trans_adc_point(self):
        """
        Translate the aerodynamic centre point along the length of the fuselage to its correct position
        :rtype: TranslatedShape
        """
        return TranslatedShape(shape_in=self.adc_point,
                               displacement=Vector(self.adc_diff,
                                                   0,
                                                   0.5 * self.cabin_diameter),
                               label='Main Wing Aerodynamic Centre')

    @Attribute
    def sweep_angle_calc(self):
        return self.obj_main_wing.obj_wingset.sweep_angle

    # ----------
    ## SAVING
    # ----------

    @gui_callable(label="Save Input Vars", icon="clone.png")
    def save_fuselage_vars(self):
        """
        This allows the user to save all variables of the current settings
        :rtype: basestring
        """
        self.save_vars
        self.obj_main_wing.save_vars
        self.def_h_tail_wing.save_vars
        self.def_v_tail_wing.save_vars
        return self.fuselage_part.save_vars

    # --------------------------
    ## This is the vertical wing
    # --------------------------

    @Attribute
    def vert_w_span(self):
        """
        This attribute calculates the desired span of the vertical wing
        :rtype: float
        """
        main_area = self.obj_main_wing.ref_area
        main_span = 2 * self.w_span
        f1 = self.root_frac
        f2 = self.vert_taper_ratio_user
        span = sqrt((2 * main_area * main_span * self.Vv) / (self.l_v * (f1 + f1 * f2)))
        return span

    @Attribute
    def z_offset(self):
        """
        Calculates the z_offset for the vertical tail such that the tip will be flush with the tail cone
        :rtype: float
        """
        x_pos = self.v_shift - (
            self.cabin_length + self.fuselage_part.length_nose)  # x-position position from start tail
        if x_pos > 0:
            x_len = self.fuselage_part.length_tail - x_pos  # X position from the back of the tail
            # Calculate the diff between tops of tail circles
            dv = self.fuselage_part.fuselage_assembly[0].edges[0].point1.z - \
                 self.fuselage_part.fuselage_assembly[0].edges[2].point1.z
            z_pos = ((dv / self.fuselage_part.length_tail) * x_len) + \
                    self.fuselage_part.fuselage_assembly[0].edges[2].point1.z  # Simple triangle calculation
            print x_len
            return z_pos
        else:
            return self.cabin_diameter

    @Part(in_tree=True)
    def def_v_tail_wing(self):
        return VTailWing(w_span=self.vert_w_span,
                         sweep_angle_user=self.vert_sweep_angle_user,
                         taper_ratio_user=self.vert_taper_ratio_user,
                         dihedral_angle_user=self.vert_dihedral_angle_user,
                         m_cruise=self.m_cruise,
                         TechFactor=self.vert_TechFactor,
                         airfoil_root=self.vert_airfoil_root,
                         airfoil_tip=self.vert_airfoil_tip,
                         d_hinge_user=self.d_hinge_user,
                         p_zero_user=self.p_zero_user,
                         p_rib_user=self.p_rib_user,
                         p_form_rib_user=self.p_form_rib_user,
                         rhl_root=self.rhl_root,
                         rhl_tip=self.rhl_tip,
                         ahl_tip=self.ahl_tip,
                         d_actuator=self.d_actuator,
                         d_front_spar=self.d_front_spar,
                         d_back_spar=self.d_back_spar,
                         pick_hinge_ribs=self.pick_hinge_ribs,
                         rud_width_frac=self.rud_width_frac,
                         rud_height_frac=self.rud_height_frac,
                         rud_length_frac=self.rud_length_frac,
                         actuator_frac=self.actuator_frac,
                         rib0_frac=self.rib0_frac,
                         rib_frac=self.rib_frac,
                         form_rib_frac=self.form_rib_frac,
                         x_offset=self.v_shift,
                         z_offset=self.z_offset,
                         root_frac=self.root_frac)

    @Part(in_tree=False)
    def extr_tail(self):
        """
        This extends the tail so that it will protrude into the spacecraft fuselage
        :rtype: ExtrudedShell
        """
        return ExtrudedShell(profile=self.def_v_tail_wing.trans_vwing.edges[0],
                             distance=self.z_offset - self.fuselage_part.fuselage_assembly[0].edges[2].point1.z + 0.05,
                             direction=(0, 0, -1))

    @Part(in_tree=False)
    def sub_tail(self):
        """
        This deletes the non visible part of the extended vertical tail that is inside the fuselage
        :rtype: SubtractedShell
        """
        return SubtractedShell(shape_in=self.extr_tail,
                               tool=[self.fuselage_part.fuselage_assembly[0],
                                     self.fuselage_part.fuselage_assembly[1]],
                               label="Fit Piece",
                               transparency=0.6,
                               color='red')

    @Attribute(in_tree=True, label="Fixed Vertical Tail")
    def fixed_v_wing(self):
        """
        Collects the two shells for the fixed tail. Prevents the use of fuse and thus making it a lot quicker
        :rtype: tuple[part]
        """
        return [self.sub_tail, self.def_v_tail_wing.fixed_part]

    @Part(in_tree=False)
    def v_adc_point(self):
        """
        Creates the point for the vertical ADC at the (0,0,0) position
        :rtype: Point
        """
        return Point(0.25 * self.def_v_tail_wing.w_c_root + self.def_v_tail_wing.mac_def[0],
                     0,
                     self.def_v_tail_wing.mac_def[1])

    @Attribute
    def v_shift(self):
        """
        This attribute calculates the distance over which the vertical tail should be shifted in lengthwise direction
        to achieve the desired l_h distance
        :rtype: float
        """
        x_main2 = self.trans_adc_point.bbox.location.x  # Get the x position of the main wing point
        shift = x_main2 - self.v_adc_point.x + self.l_v  # The shift is the difference between the points + desired l_h
        return shift

    @Part
    def trans_v_mac_line(self):
        """
        This translates the vertical MAC line to align with the vertical tail
        :rtype: TranslatedCurve
        """
        return TranslatedCurve(curve_in=self.v_mac_line,
                               displacement=Vector(self.v_shift,
                                                   0,
                                                   self.cabin_diameter),
                               color='blue',
                               line_thickness=3,
                               label='Vertical Tail MAC')

    @Part
    def trans_v_adc_point(self):
        """
        Translate the vertical ADC point to the correct position
        :rtype: TranslatedShape
        """
        return TranslatedShape(shape_in=self.v_adc_point,
                               displacement=Vector(self.v_shift,
                                                   0,
                                                   self.cabin_diameter),
                               label='Vertical Tail Aerodynamic Centre')

    @Part(in_tree=False)
    def v_mac_line(self):
        """
        Create the vertical MAC line at position (0,0,0)
        :rtype: LineSegment
        """
        return LineSegment(start=Point(0.25 * self.def_v_tail_wing.w_c_root + self.def_v_tail_wing.mac_def[0] - \
                                       0.25 * self.def_v_tail_wing.mac_def[2],
                                       0,
                                       self.def_v_tail_wing.mac_def[1]),
                           end=Point(0.25 * self.def_v_tail_wing.w_c_root + self.def_v_tail_wing.mac_def[0] + \
                                     0.75 * self.def_v_tail_wing.mac_def[2],
                                     0,
                                     self.def_v_tail_wing.mac_def[1]),
                           hidden=False)

    @Attribute
    def ver_aspect_ratio(self):
        return self.vert_w_span ** 2 / self.def_v_tail_wing.ref_area

    # -----------------
    ## HTail Wing part
    # -----------------

    @Attribute
    def l_h(self):
        """
        Calculate the distance between the ADC of the horizontal wing and the main wing ADC
        :rtype: float
        """
        return self.trans_h_adc_point.bbox.center.x - self.trans_adc_point.bbox.center.x

    @Attribute
    def hor_aspect_ratio(self):
        """
        Calculate the aspect ratio for the horizontal tail wing. Not for calculation but for reference for user
        :rype: float
        """
        return (2 * self.hor_w_span) ** 2 / self.def_h_tail_wing.ref_area

    @Attribute
    def Vh(self):
        """
        Calculate the the horizontal tail volume coefficient. Not for computations but for reference for the user.
        :rtype: float
        """
        main_area = self.obj_main_wing.ref_area  # Reference area of the main wing
        hor_area = self.def_h_tail_wing.ref_area  # Reference area of the horizontal tail wing
        main_MAC = self.trans_mac_line.length  # The length of the main wing MAC line
        Vh = (hor_area * self.l_h) / (main_area * main_MAC)  # The volume coefficient
        return Vh

    @Part(in_tree=False)
    def def_h_tail_wing(self):
        """
        Create the object for the horizontal tail wing
        :rtype: Wingset
        """
        return Wingset(w_c_root=self.h_w_c_root,
                       sweep_angle=self.hor_sweep_angle_user,
                       taper_ratio=self.hor_taper_ratio_user,
                       dihedral_angle=self.hor_dihedral_angle_user,
                       m_cruise=self.m_cruise,
                       TechFactor=self.hor_TechFactor,
                       w_span=self.hor_w_span,
                       airfoil_root=self.hor_airfoil_root,
                       airfoil_tip=self.hor_airfoil_tip,
                       save_name="htail.csv")

    @Part(in_tree=False)
    def rotate_h_tail_wing(self):
        """
        Rotate the wing from a vertical position to a horizontal position
        :rtype: RotatedShape
        """
        return RotatedShape(shape_in=self.def_h_tail_wing.wingset[child.index],
                            rotation_point=Point(0, 0, 0),
                            vector=Vector(1, 0, 0),
                            angle=radians(90),
                            quantify=2
                            )

    @Part(in_tree=True)
    def translate_h_tail_wing(self):
        """
        Translate the wing so that its front aligns with the front of the vertical tail and that it fits on top
        :rtype: TranslatedShape
        """
        return TranslatedShape(shape_in=self.rotate_h_tail_wing[child.index],
                               displacement=Vector(
                                   self.fixed_v_wing[1].edges[8].midpoint.x,
                                   0,
                                   self.fixed_v_wing[1].edges[8].midpoint.z),
                               quantify=2,
                               label=['Right Side', 'Left Side'][child.index])

    @Part(in_tree=False)
    def h_adc_point(self):
        """
        Create the horizontal tail wing aerodynamic centre point at ref position (0,0,0)
        :rtype: Point
        """
        return Point(0.25 * self.h_w_c_root + self.def_h_tail_wing.mac_def[0],
                     0,
                     0)

    @Part
    def h_mac_line(self):
        """
        Create the horizontal tail wing mean aerodynamic chord line at ref position (0,0,0)
        :rtype: LineSegment
        """
        return LineSegment(start=Point(0.25 * self.h_w_c_root + self.def_h_tail_wing.mac_def[0] -
                                       0.25 * self.def_h_tail_wing.mac_def[2],
                                       0,
                                       0),
                           end=Point(0.25 * self.h_w_c_root + self.def_h_tail_wing.mac_def[0] +
                                     0.75 * self.def_h_tail_wing.mac_def[2],
                                     0,
                                     0),
                           hidden=True)

    @Part
    def trans_h_mac_line(self):
        """
          Create the horizontal tail wing MAC line to the correct position
          :rtype: TranslatedCurve
          """
        return TranslatedCurve(curve_in=self.h_mac_line,
                               displacement=Vector(
                                   self.fixed_v_wing[1].edges[8].midpoint.x,
                                   0,
                                   0.5*self.cabin_diameter),
                               color='blue',
                               line_thickness=3,
                               label='Horizontal Tail MAC')

    @Part
    def trans_h_adc_point(self):
        """
          Translate the horizontal tail wing aerodynamic centre point to the correct position
          :rtype: TranslatedShape
          """
        return TranslatedShape(shape_in=self.h_adc_point,
                               displacement=Vector(
                                   self.fixed_v_wing[1].edges[8].midpoint.x,
                                   0,
                                   0.5*self.cabin_diameter),
                               label='Horizontal Tail Aerodynamic Centre')

    # --------------------
    ## AVL and Force Part
    # --------------------

    @Part
    def interface(self):
        return avl.Interface(filename="FullAircraft",
                             directory="output",
                             geometry=geometry(self),
                             outputs=["fs", "fn", "fe"],
                             close_when_done=True,
                             if_exists="overwrite"
                             )

    @Attribute
    def hinge_side_force(self):
        """
        calculate the side force and distributed load due to the aerodynamic load
        :rtype: tuple[float]
        """
        cy_dict = self.interface.surface_forces  # Create dictionary from AVL
        cy = cy_dict["surfaces"]["Rudder"]["CY"]  # Side force coefficient
        s_ref = cy_dict["surfaces"]["Rudder"]["Ssurf"]  # Reference area
        q_dyn = 0.5 * self.rho * (self.m_cruise * 340) ** 2  # Dynamic pressure
        Fy = cy * q_dyn * s_ref * self.FoS  # Side Force
        q = Fy / self.def_v_tail_wing.b_rudder  # Distributed Load
        return Fy, q

    @Attribute
    def hinge_reaction_forces(self):
        """
        calculates the reaction forces per hinge [N]
        Note that this DOES NOT include the forces due to the actuators yet
        :rtype: list
        """
        q = self.hinge_side_force[1]  # The distributed load
        R = []  # An empty list
        l = []  # An empty list
        for x in range(0, len(self.def_v_tail_wing.hinges)):
            # The below loop determines the midpoints between each hinge and then the lengths between them.
            # It uses these lengths to calculate the hinge reaction forces due to aerodynamic pressure
            ref = self.def_v_tail_wing.closure_ribs[0].vertices[0].point.z #Bottom of the rudder
            top_ref = self.def_v_tail_wing.closure_ribs[1].vertices[0].point.z
            if x == 0:  # For the first hinge the distance is between the edge and midpoint
                p2_z = self.def_v_tail_wing.hinges[x].center.z
                p1_z = ref
                p3_z = self.def_v_tail_wing.hinges[x + 1].center.z
                pmid_z = p3_z - 0.5 * (p3_z - p2_z)
                length = pmid_z - p1_z
                l.append(length)
                force = - q * length
                R.append(force)
            elif x > 0 and x < (len(self.def_v_tail_wing.hinges) - 1):  # All the middle hinges
                p1_z = pmid_z  # Take the previous midpoint and set it as bottom
                p2_z = self.def_v_tail_wing.hinges[x].center.z # Take the position of current hinge
                p3_z = self.def_v_tail_wing.hinges[x + 1].center.z # Take position of the next hinge
                pmid_z = p3_z - 0.5 * (p3_z - p2_z)  # Position middle of current and next hinge
                length = pmid_z - p1_z  # Length is current middle - last middle
                l.append(length)  # Append length list
                force = - q * length
                R.append(force)
            elif x == (
                        len(
                            self.def_v_tail_wing.hinges) - 1):  # For the last hinge the distance is between midpoint and edge
                length = top_ref - pmid_z  # The length of the last part, total - last mid
                l.append(length)  # Append lengths
                force = - q * length  # Calculate force
                R.append(force)  # Append force
        check = (sum(l) - (top_ref - ref) == 0)  # Checks if the calculations of l are valid
        print l
        if check != True:
            warnings.warn('Something went wrong in the hinge reaction forces, check is false')

        return R

    @Attribute
    def actuator_forces(self):
        """
        Calculates the actuator force [N] and moment [Nm]
        :rtype: float
        """
        d_hl = self.def_v_tail_wing.d_hinge * self.x_fc  # arm over which force F acts
        M_f = self.hinge_side_force[0] * d_hl  # Moment due to side force
        point_act = self.def_v_tail_wing.actuator_hinge_line.midpoint  # Point on act line
        point_hinge = self.def_v_tail_wing.hingerib_line.midpoint  # point on hinge line
        # Point to line distance
        min_1 = point_act - self.def_v_tail_wing.hingerib_line.start
        min_2 = point_act - self.def_v_tail_wing.hingerib_line.end
        d1 = self.def_v_tail_wing.hingerib_line.start.distance(self.def_v_tail_wing.hingerib_line.end)
        d = numpy.cross(min_1,min_2)/d1
        da = d[0]
        Fa = M_f / da  # The actuator Force [N]
        Fa_x = - Fa * cos(radians(self.rud_angle))
        Fa_y = Fa * sin(radians(self.rud_angle))
        distance = self.force_distances
        F1 = - Fa * distance[0][0] / sum(distance[0])  # Force on nearest hinge
        # F1_x = - F1 * cos(radians(self.rud_angle))
        F1_x = - Fa_x * distance[0][0] / sum(distance[0])
        F1_y = F1 * sin(radians(self.rud_angle))
        F2 = - Fa * distance[0][1] / sum(distance[0])  # Force on second nearest hinge
        # F2_x = - F2 * cos(radians(self.rud_angle))
        F2_x = - Fa_x * distance[0][1] / sum(distance[0])
        F2_y = F2 * sin(radians(self.rud_angle))
        Fh = [[F1_x, F1_y], [F2_x, F2_y], distance[1]]  # Forces and their corresponding hinge numbers
        check_x = (F1_x + F2_x) + Fa_x
        print check_x
        return [Fa_x, Fa_y], Fh, M_f

    @Attribute
    def force_distances(self):
        """
        Calculates the distance between the actuator force and the nearest two hinges
        :rtype: float
        """
        force_point = self.def_v_tail_wing.actuator_hinge_line.midpoint
        distances = []
        distances_up = []
        distances_down = []
        for x in range(0, len(self.def_v_tail_wing.hinges)):
            # First look at all the hinges above the actuator
            distances.append(force_point.distance(self.def_v_tail_wing.hinges[x].center))
            if self.def_v_tail_wing.hinges[x].center.z > force_point.z:
                dist_up = force_point.distance(self.def_v_tail_wing.hinges[x].center)
                distances_up.append(dist_up)
            # Look at the hinges below the actuator
            else:
                dist_down = force_point.distance(self.def_v_tail_wing.hinges[x].center)
                distances_down.append(dist_down)
        shortest_up = sorted(distances_up)[0]       # Finds the shortest distance up
        shortest_down = sorted(distances_down)[0]   # Finds the shortest distance down
        hinge_number = []
        hinge_number.append(distances.index(shortest_down))  # Find the hinge number of the first distance
        hinge_number.append(distances.index(shortest_up))  # Find the hinge number of the second distance
        shortest = [shortest_down, shortest_up]
        return shortest, hinge_number

    @Attribute
    def total_hinge_force(self):
        """
        This computes the total forces per hinge. This is the aerodynamic forces per hinge and the forces on
        two hinges due to the actuators. The actuator attribute also outputs the hinge numbers on which it acts
        so this makes it easy to compute
        :rtype: tuple[float]
        """
        aero_force = self.hinge_reaction_forces  # The forces on all hinges due to aerodynamic load
        act_force = self.actuator_forces  # The forces on some actuators due to actuator force
        tot_force_y = []
        for item in aero_force:
            tot_force_y.append(item)    # Aerodynamic load only works in y direction
        tot_force_x = [0] * len(tot_force_y)# To be filled with y forces in the actuator forces
        tot_force = [0] * len(tot_force_y)  # The total forces
        for index in range(0, len(tot_force_y)):   # Loop over the range of the forces
            if index == act_force[1][2][0]: # If we are at the first actuator hinge
                print tot_force_y[index]
                tot_force_y[index] = tot_force_y[index] + act_force[1][0][1]    # Add the y force to the current
                print tot_force_y[index]
                print act_force[1][0][1]
                tot_force_x[index] = tot_force_x[index] + act_force[1][0][0]    # Add the x force to the current
            if index == act_force[1][2][1]:
                tot_force_y[index] = tot_force_y[index] + act_force[1][1][1]
                tot_force_x[index] = tot_force_x[index] + act_force[1][1][0]
            tot_force[index] = sqrt(tot_force_y[index]**2 + tot_force_x[index]**2)
        return tot_force, tot_force_x, tot_force_y

    @Attribute
    def hinge_mass(self):
        """
        Compute the hinge masses for a single load path hinge [kg]
        :rtype: tuple[float]
        """
        h = self.def_v_tail_wing.d_front_spar * 1000  # in mm
        weight = []
        for x in range(0, len(self.total_hinge_force[0])):
            mass = 0.110 * (1 + (abs(self.total_hinge_force[0][x]) / 30000)) * ((h / 100) + 1)
            weight.append(mass)
        return weight

    @Attribute
    def rudder_weight(self):
        """
        Calls the Apply Material class and returns the weight of the rudder
        :rtype: float
        """
        obj = ApplyMat(is_default=True,
                       hinge_forces=self.total_hinge_force[0],
                       obj=self)
        return obj.weights

    #     # @Attribute(in_tree=False)
    #     # def total_length(self):
    #     #     return self.fuselage_part.fuselage_length
    #     #


    #     #


    #     #

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

    @Attribute
    def force_lines(self):
        return ForceLines(craft=self)

    @Attribute
    def sorted_ribs(self):
        return sorted(self.def_v_tail_wing.rudder_ribs,  key=lambda face: face.cog.z)

    @Attribute
    def bays (self):
        list = []
        list.append(TranslatedPlane(built_from=self.def_v_tail_wing.closure_ribs[0].u_reversed,
                                 displacement=Vector(0, 0, 0.01)))
        for i in xrange(len(self.sorted_ribs)):
            list.append(self.sorted_ribs[i].u_reversed)
        list.append(TranslatedPlane(built_from=self.def_v_tail_wing.closure_ribs[1].u_reversed,
                                    displacement=Vector(0, 0, -0.01)))
        return list

    @Attribute
    def positions_planes(self):
        list = []
        dx = self.dx
        for i in xrange(len(self.bays)):
            list.append(int((self.bays[i].uv_center_point.z- self.def_v_tail_wing.closure_ribs[0].vertices[0].point.z)/dx))

        return list

    @Attribute
    def rhs_skin_faces(self):
        return [self.def_v_tail_wing.fused_le_skin_right.shells[0], self.def_v_tail_wing.main_skin_right.faces[0],
                self.def_v_tail_wing.te_skin_right.faces[0]]

    @Attribute
    def lhs_skin_faces(self):
        return [self.def_v_tail_wing.fused_le_skin_left.shells[0], self.def_v_tail_wing.main_skin_left.faces[0],
                self.def_v_tail_wing.te_skin_left.faces[0]]

    @Attribute
    def spar_faces(self):
        return [self.def_v_tail_wing.rudder_front_spar.faces[0], self.def_v_tail_wing.rudder_back_spar.faces[0]]

    @Attribute
    def bay_analysis(self):
        quasi = ReadMaterial(ply_file="quasi_isotropic.csv").read
        forty_five = ReadMaterial(ply_file="forty_five.csv").read
        obj = ApplyMat(is_default= True,
                       hinge_forces=self.total_hinge_force[0],
                       obj=self)
        analysis = []

        for i in xrange(len(self.bays)-1):
            analysis.append( BayAnalysis(Vx=[self.force_lines.force_lines[0][i],self.force_lines.force_lines[0][i+1]],
                               Vy=[self.force_lines.force_lines[1][i],self.force_lines.force_lines[1][i+1]],
                               Mx=[self.force_lines.force_lines[2][i],self.force_lines.force_lines[2][i+1]],
                               My=[self.force_lines.force_lines[3][i],self.force_lines.force_lines[3][i+1]],
                               Mt=[self.force_lines.force_lines[4][i],self.force_lines.force_lines[4][i+1]],
                               ref_x=[0] * 2,
                               ref_y=[0] * 2,
                               bay_planes=[self.bays[i],self.bays[i+1]],
                               rhs_skin_faces=self.lhs_skin_faces,
                               lhs_skin_faces=self.rhs_skin_faces,
                               spar_faces=self.spar_faces,
                               rhs_skin_materials_t=[forty_five[str(obj.n_LE)]['t'],forty_five[str(obj.n_main)]['t'],forty_five[str(obj.n_TE)]['t']] ,
                               lhs_skin_materials_t=[forty_five[str(obj.n_LE)]['t'],forty_five[str(obj.n_main)]['t'],forty_five[str(obj.n_TE)]['t']],
                               spar_materials_t=[quasi[str(obj.n_spar[0])]['t'],quasi[str(obj.n_spar[1])]['t']],
                               rhs_skin_materials_E=[forty_five[str(obj.n_LE)]['E'],forty_five[str(obj.n_main)]['E'],forty_five[str(obj.n_TE)]['E']],
                               lhs_skin_materials_E=[forty_five[str(obj.n_LE)]['E'],forty_five[str(obj.n_main)]['E'],forty_five[str(obj.n_TE)]['E']],
                               spar_materials_E=[quasi[str(obj.n_spar[0])]['E'],quasi[str(obj.n_spar[1])]['E']],
                               rhs_skin_materials_G=[forty_five[str(obj.n_LE)]['G'],forty_five[str(obj.n_main)]['G'],forty_five[str(obj.n_TE)]['G']],
                               lhs_skin_materials_G=[forty_five[str(obj.n_LE)]['G'],forty_five[str(obj.n_main)]['G'],forty_five[str(obj.n_TE)]['G']],
                               spar_materials_G=[quasi[str(obj.n_spar[0])]['G'],quasi[str(obj.n_spar[1])]['G']],
                               rhs_skin_materials_D=[[forty_five[str(obj.n_LE)]['D11'], forty_five[str(obj.n_LE)]['D22'], forty_five[str(obj.n_LE)]['D22'], forty_five[str(obj.n_LE)]['D12']],
                                                     [forty_five[str(obj.n_main)]['D11'], forty_five[str(obj.n_main)]['D22'], forty_five[str(obj.n_main)]['D22'], forty_five[str(obj.n_main)]['D12']],
                                                     [forty_five[str(obj.n_TE)]['D11'], forty_five[str(obj.n_TE)]['D22'], forty_five[str(obj.n_TE)]['D22'], forty_five[str(obj.n_TE)]['D12']]],
                               lhs_skin_materials_D=[[forty_five[str(obj.n_LE)]['D11'], forty_five[str(obj.n_LE)]['D22'], forty_five[str(obj.n_LE)]['D22'], forty_five[str(obj.n_LE)]['D12']],
                                                     [forty_five[str(obj.n_main)]['D11'], forty_five[str(obj.n_main)]['D22'], forty_five[str(obj.n_main)]['D22'], forty_five[str(obj.n_main)]['D12']],
                                                     [forty_five[str(obj.n_TE)]['D11'], forty_five[str(obj.n_TE)]['D22'], forty_five[str(obj.n_TE)]['D22'], forty_five[str(obj.n_TE)]['D12']]],
                               spar_materials_D=[[quasi[str(obj.n_spar[0])]['D11'], quasi[str(obj.n_spar[0])]['D22'], quasi[str(obj.n_spar[0])]['D22'], quasi[str(obj.n_spar[0])]['D12']],
                                                 [quasi[str(obj.n_spar[1])]['D11'], quasi[str(obj.n_spar[1])]['D22'], quasi[str(obj.n_spar[1])]['D22'], quasi[str(obj.n_spar[1])]['D12']]],
                               N=3) )
        return analysis



    @Part(in_tree=True)
    def fuse_fuselage(self):
        """
        Fuses together the solids of the fuselage
        :rtype: FusedSolid
        """
        return FusedSolid(shape_in=self.fuselage_part.fuselage_assembly[1],
                          tool=[self.fuselage_part.fuselage_assembly[0], self.fuselage_part.fuselage_assembly[2]])

    @Part(in_tree=True)
    def wet_wings_left(self):
        return SubtractedSolid(shape_in=self.main_wing[0],
                               tool = self.fuse_fuselage)
    @Part(in_tree=True)
    def wet_wings_right(self):
        return SubtractedSolid(shape_in=self.main_wing[1],
                               tool = self.fuse_fuselage)


    @Attribute
    def rudder_nodes(self):
        tail = self.def_v_tail_wing
        list = [tail.skins_rudder,
                tail.rudder_back_spar,
                tail.rudder_front_spar,
                tail.actuator_hinge_line,
                tail.hingerib_line,
                tail.closure_ribs[0],
                tail.closure_ribs[1],
                tail.actuator_hinges[0],
                tail.actuator_hinges[1]]
        for x in range(0, len(tail.rudder_ribs)):
            list.append(tail.rudder_ribs[x])
        for x in range(0, len(tail.hinges)):
            list.append(tail.hinges[x])
        return list

    @Part()
    def rudder_writer(self):
        return STEPWriter(nodes=self.rudder_nodes,
                          default_directory='../output/CAD')
    @Attribute
    def wetted_nodes(self):
        list = [self.fixed_v_wing[0],
                self.fixed_v_wing[1],
                self.translate_h_tail_wing[0],
                self.translate_h_tail_wing[1],
                self.def_v_tail_wing.skins_rudder,
                self.fuse_fuselage,
                self.wet_wings_left,
                self.wet_wings_right]
        return list
    @Part
    def wetted_writer(self):
        return STEPWriter(nodes=self.wetted_nodes,
                          default_directory='../output/CAD')
    @Attribute
    def wetted_area(self):
        main_wings = 2 * (self.wet_wings_left.faces[0].area + self.wet_wings_left.faces[1].area)
    @Attribute
    def save_vars(self):
        """ Saves the variables of current settings to an output file
        :rtype: string and csv
        """
        path = csvr.generate_path("constants.csv")
        first_row = True
        with open(path[0], 'rb') as file:  # Open file
            reader = csv.reader(file, delimiter=',', quotechar='|')  # Read into reader and section rows and columns
            with open(path[1], 'wb') as outfile:
                filewriter = csv.writer(outfile, delimiter=',', quotechar='|')
                for row in reader:
                    if first_row == True:
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

    obj = Aircraft()
    display(obj)
