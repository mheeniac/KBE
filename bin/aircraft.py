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
    l_v = Input(const["l_v"])

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
    d_hinge_user = Input(vtail["d_hinge_user"])  # Overwrites the default function if ~= 'NaN'

    #: Distance in z direction of first fin rib with respect to the root[m]
    #: :type: float
    p_zero_user = Input(vtail["p_zero_user"])  # Overwrites the default function if ~= 'NaN'

    #: Distance in z direction of following fin ribs with respect to the previous one [m]
    #: :type: float
    p_rib_user = Input(vtail["p_rib_user"])  # Overwrites the default function if ~= 'NaN'

    #: Distance in z direction of the form rib with respect to the first form rib [m]
    #: :type: float
    p_form_rib_user = Input(vtail["p_form_rib_user"])  # Overwrites the default function if ~= 'NaN'

    #: Ratio of local width where the local hinge is located []
    #: :type: float
    rhl_root = Input(vtail["rhl_root"])

    #: Ratio of local width where the local hinge is located []
    #: :type: float
    rhl_tip = Input(vtail["rhl_tip"])

    #: Ratio of local width where the local actuator hinge is located []
    #: :type: float
    ahl_tip = Input(vtail["ahl_tip"])

    #: Distance in z direction between the to actuator hinge planes [m]
    #: :type: float
    d_actuator = Input(vtail["d_actuator"])

    #: Distance of front spar with respect to the hinge plane [m]
    #: :type: float
    d_front_spar = Input(vtail["d_front_spar"])

    #: Distance of back spar with respect to the trailing edge [m]
    #: :type: float
    d_back_spar = Input(vtail["d_back_spar"])

    #: Select which ribs are the hinge ribs. Default value is [1,2,3,4,5,6] al hinges are used. []
    #: :type: list of integers
    pick_hinge_ribs = Input([2, 4, 5, 6])

    #: Rudder size fraction. Rudder width/Fin root chord []
    #: :type: float
    rud_width_frac = Input(vtail["rud_width_frac"])

    #: The height offset of the rudder from the bottom of the fin (height offset/first rib height) []
    #: :type: float
    rud_height_frac = Input(vtail["rud_height_frac"])

    #: The fraction of the length of the rudder (rudder length/fin span) []
    #: :type: float
    rud_length_frac = Input(vtail["rud_length_frac"])

    #: The fraction of the height of the actuator box from the bottom (box height/fin span)
    #: If you want the actuator n ribs lower or higher just input 0.33 +/- p_rib*n
    #: :type: float
    actuator_frac = Input(vtail["actuator_frac"])

    #: The fraction of the height of the first rib from the bottom (rib height/fin span) []
    #: :type: float
    rib0_frac = Input(vtail["rib0_frac"])

    #: The fraction of the height of the ribs (rib height/fin span) []
    #: :type: float
    rib_frac = Input(vtail["rib_frac"])

    #: The fraction of the height of the form ribs (form rib height/fin span) []
    #: :type: float
    form_rib_frac = Input(vtail["form_rib_frac"])

    #: Iteration size of to make the shear and bend moment lines [m]
    #: :type: float
    dx = Input(const["dx"])

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
    hor_TechFactor = Input(htail["TechFactor"])  # Technology factor is equal to 0.87 NACA 6 airfoil and 1 to other conventional airfoils

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

    # Overwrite optimization
    #: :type: Bool
    override = Input(False)

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
                       sweep_angle_user=self.sweep_angle,
                       taper_ratio_user=self.taper_ratio,
                       dihedral_angle_user=self.dihedral_angle,
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
                                   self.adc_diff(),  # Translate along fuselage length with calculated difference
                                   0,
                                   self.obj_main_wing.calc_lowest_point+0.01),  # Translate down so that it is bottom wing
                               quantify=2,
                               color='red',
                               label=['Left Wing', 'Right Wing'][child.index]
                               )

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
                               displacement=Vector(self.adc_diff(),
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
                               displacement=Vector(self.adc_diff(),
                                                   0,
                                                   0.5 * self.cabin_diameter),
                               label='Main Wing Aerodynamic Centre')

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
        self.save_vars()
        self.obj_main_wing.save_vars
        self.def_h_tail_wing.save_vars
        self.def_v_tail_wing.save_vars
        return self.fuselage_part.save_vars

    # --------------------------
    ## This is the vertical wing
    # --------------------------

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

    def z_offset(self):
        """
        Calculates the z_offset for the vertical tail such that the tip will be flush with the tail cone
        :rtype: float
        """
        x_pos = self.v_shift() - (self.cabin_length + self.fuselage_part.length_nose)  # x-position position from start tail
        if x_pos > 0:
            x_len = self.fuselage_part.length_tail - x_pos  # X position from the back of the tail
            # Calculate the diff between tops of tail circles
            dv = self.fuselage_part.fuselage_assembly[0].edges[0].point1.z - \
                 self.fuselage_part.fuselage_assembly[0].edges[2].point1.z
            z_pos = ((dv / self.fuselage_part.length_tail) * x_len) + \
                    self.fuselage_part.fuselage_assembly[0].edges[2].point1.z  # Simple triangle calculation
            return z_pos
        else:
            return self.cabin_diameter

    @Part(in_tree=True)
    def def_v_tail_wing(self):
        return VTailWing(w_span=self.vert_w_span(),
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
                         x_offset=self.v_shift(),
                         z_offset=self.z_offset(),
                         root_frac=self.root_frac)

    @Part(in_tree=False)
    def extr_tail(self):
        """
        This extends the tail so that it will protrude into the spacecraft fuselage
        :rtype: ExtrudedShell
        """
        return ExtrudedShell(profile=self.def_v_tail_wing.trans_vwing.edges[0],
                             distance=self.z_offset() - self.fuselage_part.fuselage_assembly[0].edges[2].point1.z + 0.05,
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
                               displacement=Vector(self.v_shift(),
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
                               displacement=Vector(self.v_shift(),
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
        return self.vert_w_span() ** 2 / self.def_v_tail_wing.ref_area

    # -----------------
    ## HTail Wing part
    # -----------------

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
        Vh = (hor_area * self.l_h()) / (main_area * main_MAC)  # The volume coefficient
        return Vh

    @Part(in_tree=False)
    def def_h_tail_wing(self):
        """
        Create the object for the horizontal tail wing
        :rtype: Wingset
        """
        return Wingset(w_c_root=self.h_w_c_root,
                       sweep_angle_user=self.hor_sweep_angle_user,
                       taper_ratio_user=self.hor_taper_ratio_user,
                       dihedral_angle_user=self.hor_dihedral_angle_user,
                       m_cruise=self.m_cruise,
                       TechFactor=self.hor_TechFactor,
                       w_span=self.hor_w_span,
                       airfoil_root=self.hor_airfoil_root,
                       airfoil_tip=self.hor_airfoil_tip,
                       main_sweep = self.obj_main_wing.obj_wingset.sweep_angle,
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

    def hinge_reaction_forces(self):
        """
        calculates the reaction forces per hinge [N]
        Note that this DOES NOT include the forces due to the actuators yet
        :rtype: list
        """
        q = self.hinge_side_force()[1]  # The distributed load
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
        M_f = self.hinge_side_force()[0] * d_hl  # Moment due to side force
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
        distance = self.force_distances()
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
        return [Fa_x, Fa_y], Fh, M_f


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
        aero_force = self.hinge_reaction_forces()  # The forces on all hinges due to aerodynamic load
        act_force = self.actuator_forces  # The forces on some actuators due to actuator force
        tot_force_y = []
        for item in aero_force:
            tot_force_y.append(item)    # Aerodynamic load only works in y direction
        tot_force_x = [0] * len(tot_force_y)# To be filled with y forces in the actuator forces
        tot_force = [0] * len(tot_force_y)  # The total forces
        for index in range(0, len(tot_force_y)):   # Loop over the range of the forces
            if index == act_force[1][2][0]: # If we are at the first actuator hinge
                tot_force_y[index] = tot_force_y[index] + act_force[1][0][1]    # Add the y force to the current
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
        act_force = sqrt(self.actuator_forces[0][1]**2 + self.actuator_forces[0][0] ** 2)
        act_weight = [0.110 * (1 + (abs(0.5*act_force) / 30000)) * ((h / 100) + 1)] * 2
        return weight, act_weight

    @Attribute
    def rudder_weight(self):
        """
        Calls the Apply Material class and returns the weight of the rudder
        :rtype: float
        """
        obj = ApplyMat(is_default=True,
                       hinge_forces=self.total_hinge_force[0],
                       obj=self,
                       n_plies = self.n_ply_list,
                       mat_dict = self.optimise_material[1])
        return obj.weights + sum(self.hinge_mass[0]) + sum(self.hinge_mass[1])

    @Attribute(in_tree=False)
    def total_length(self):
        return self.fuselage_part.fuselage_length


    @Attribute
    def force_lines(self):
        return ForceLines(craft=self)

    def sorted_ribs(self):
        return sorted(self.def_v_tail_wing.rudder_ribs,  key=lambda face: face.cog.z)

    @Attribute
    def bays (self):
        list = []
        list.append(TranslatedPlane(built_from=self.def_v_tail_wing.closure_ribs[0].u_reversed,
                                 displacement=Vector(0, 0, 0.01)))
        for i in xrange(len(self.sorted_ribs())):
            list.append(self.sorted_ribs()[i].u_reversed)
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

    def rhs_skin_faces(self):
        return [self.def_v_tail_wing.fused_le_skin_right, self.def_v_tail_wing.main_skin_right.faces[0],
                self.def_v_tail_wing.te_skin_right.faces[0]]

    def lhs_skin_faces(self):
        return [self.def_v_tail_wing.fused_le_skin_left, self.def_v_tail_wing.main_skin_left.faces[0],
                self.def_v_tail_wing.te_skin_left.faces[0]]

    def spar_faces(self):
        return [self.def_v_tail_wing.rudder_front_spar.faces[0], self.def_v_tail_wing.rudder_back_spar.faces[0]]

    @Input(settable=True)
    def n_ply_list(self):
        length = len(self.bays) - 1
        n_ply_rhs_LE = [8] * length
        n_ply_rhs_main = [10] * length
        n_ply_rhs_TE = [4] * length
        n_ply_lhs_LE = [8] * length
        n_ply_lhs_main = [10] * length
        n_ply_lhs_TE = [4] * length
        n_ply_front_spar = [8] * length
        n_ply_back_spar = [8] * length
        return n_ply_rhs_LE,n_ply_rhs_main,n_ply_rhs_TE,n_ply_lhs_LE,n_ply_lhs_main,n_ply_lhs_TE,n_ply_front_spar,n_ply_back_spar

    @Attribute
    def ref_y(self):
        y = []
        for i in xrange(len(self.bays)):
            ref = self.def_v_tail_wing.hingerib_line.start.y +self.def_v_tail_wing.hingerib_line.direction_vector.y/self.def_v_tail_wing.hingerib_line.direction_vector.z*(self.def_v_tail_wing.hingerib_line.start.z-self.bays[i].uv_center_point.z)
            y.append(ref)
        return y


    def bay_analysis(self, mat,n_ply_list):
        analysis = []
        for i in xrange(len(self.bays)-1):
            analysis.append( BayAnalysis(Vx=[self.force_lines.force_lines[0][self.positions_planes[i]],self.force_lines.force_lines[0][self.positions_planes[i+1]]],
                               Vy=[self.force_lines.force_lines[1][self.positions_planes[i]],self.force_lines.force_lines[1][self.positions_planes[i+1]]],
                               Mx=[self.force_lines.force_lines[2][self.positions_planes[i]],self.force_lines.force_lines[2][self.positions_planes[i+1]]],
                               My=[self.force_lines.force_lines[3][self.positions_planes[i]],self.force_lines.force_lines[3][self.positions_planes[i+1]]],
                               Mt=[self.force_lines.force_lines[4][self.positions_planes[i]],self.force_lines.force_lines[4][self.positions_planes[i+1]]],
                               ref_x=[self.def_v_tail_wing.d_hinge] * 2,
                               ref_y=[self.ref_y[i],self.ref_y[i+1]],
                               bay_planes=[self.bays[i],self.bays[i+1]],
                               rhs_skin_faces=self.lhs_skin_faces(),
                               lhs_skin_faces=self.rhs_skin_faces(),
                               spar_faces=self.spar_faces(),
                               rhs_skin_materials_t=[mat[0][str(n_ply_list[0][i])]['t'],mat[1][str(n_ply_list[1][i])]['t'],mat[2][str(n_ply_list[2][i])]['t']] ,
                               lhs_skin_materials_t=[mat[3][str(n_ply_list[3][i])]['t'],mat[4][str(n_ply_list[4][i])]['t'],mat[5][str(n_ply_list[5][i])]['t']],
                               spar_materials_t=[mat[6][str(n_ply_list[6][i])]['t'],mat[7][str(n_ply_list[7][i])]['t']],
                               rhs_skin_materials_E=[mat[0][str(n_ply_list[0][i])]['E'],mat[1][str(n_ply_list[1][i])]['E'],mat[2][str(n_ply_list[2][i])]['E']],
                               lhs_skin_materials_E=[mat[3][str(n_ply_list[3][i])]['E'],mat[4][str(n_ply_list[4][i])]['E'],mat[5][str(n_ply_list[5][i])]['E']],
                               spar_materials_E=[mat[6][str(n_ply_list[6][i])]['E'],mat[7][str(n_ply_list[7][i])]['E']],
                               rhs_skin_materials_G=[mat[0][str(n_ply_list[0][i])]['G'],mat[1][str(n_ply_list[1][i])]['G'],mat[2][str(n_ply_list[2][i])]['G']],
                               lhs_skin_materials_G=[mat[3][str(n_ply_list[3][i])]['G'],mat[4][str(n_ply_list[4][i])]['G'],mat[5][str(n_ply_list[5][i])]['G']],
                               spar_materials_G=[mat[6][str(n_ply_list[6][i])]['G'],mat[7][str(n_ply_list[7][i])]['G']],
                               rhs_skin_materials_D=[[mat[0][str(n_ply_list[0][i])]['D11'], mat[0][str(n_ply_list[0][i])]['D22'], mat[0][str(n_ply_list[0][i])]['D22'], mat[0][str(n_ply_list[0][i])]['D12']],
                                                     [mat[1][str(n_ply_list[1][i])]['D11'], mat[1][str(n_ply_list[1][i])]['D22'], mat[1][str(n_ply_list[1][i])]['D22'], mat[1][str(n_ply_list[1][i])]['D12']],
                                                     [mat[2][str(n_ply_list[2][i])]['D11'], mat[2][str(n_ply_list[2][i])]['D22'], mat[2][str(n_ply_list[2][i])]['D22'], mat[2][str(n_ply_list[2][i])]['D12']]],
                               lhs_skin_materials_D=[[mat[3][str(n_ply_list[3][i])]['D11'], mat[3][str(n_ply_list[3][i])]['D22'], mat[3][str(n_ply_list[3][i])]['D22'], mat[3][str(n_ply_list[3][i])]['D12']],
                                                     [mat[1][str(n_ply_list[4][i])]['D11'], mat[1][str(n_ply_list[4][i])]['D22'], mat[1][str(n_ply_list[4][i])]['D22'], mat[1][str(n_ply_list[4][i])]['D12']],
                                                     [mat[5][str(n_ply_list[5][i])]['D11'], mat[5][str(n_ply_list[5][i])]['D22'], mat[5][str(n_ply_list[5][i])]['D22'], mat[5][str(n_ply_list[5][i])]['D12']]],
                               spar_materials_D=[[mat[6][str(n_ply_list[6][i])]['D11'], mat[6][str(n_ply_list[6][i])]['D22'], mat[6][str(n_ply_list[6][i])]['D22'], mat[6][str(n_ply_list[6][i])]['D12']],
                                                 [mat[7][str(n_ply_list[7][i])]['D11'], mat[7][str(n_ply_list[7][i])]['D22'], mat[7][str(n_ply_list[7][i])]['D22'], mat[7][str(n_ply_list[7][i])]['D12']]],
                               N=3) )
        return analysis
        

    @Attribute
    def optimise_material(self):
        quasi = ReadMaterial(ply_file="quasi_isotropic.csv").read
        forty_five = ReadMaterial(ply_file="forty_five.csv").read
        zero_ninety = ReadMaterial(ply_file="zero_ninety.csv").read

        if self.override == True:
            p = 3
        else:
            p = 4

        for k in range(1,p):
            if k == 1:
                mat_dict = [0] * 8
                mat_dict[0] = forty_five
                mat_dict[1] = forty_five
                mat_dict[2] = forty_five
                mat_dict[3] = forty_five
                mat_dict[4] = forty_five
                mat_dict[5] = forty_five
                mat_dict[6] = forty_five
                mat_dict[7] = forty_five
                n_ply_list = self.n_ply_list
                bay = self.bay_analysis(mat=mat_dict,n_ply_list = n_ply_list)
                comp_rhs_le = []
                comp_rhs_main = []
                comp_rhs_te = []
                comp_lhs_le = []
                comp_lhs_main = []
                comp_lhs_te = []
                comp_front_spar = []
                comp_back_spar = []
                
                shear_rhs_le = []
                shear_rhs_main = []
                shear_rhs_te = []
                shear_lhs_le = []
                shear_lhs_main = []
                shear_lhs_te = []
                shear_front_spar = []
                shear_back_spar = []
                
                for sections in bay:
                    comp = sections.max_compression_lst
                    shear = sections.max_shear_lst
                    comp_rhs_le.append(comp[0])
                    comp_rhs_main.append(comp[1])
                    comp_rhs_te.append(comp[2])
                    comp_lhs_le.append(comp[3])
                    comp_lhs_main.append(comp[4])
                    comp_lhs_te.append(comp[5])
                    comp_front_spar.append(comp[6])
                    comp_back_spar.append(comp[7])
                    
                    shear_rhs_le.append(shear[0])
                    shear_rhs_main.append(shear[1])
                    shear_rhs_te.append(shear[2])
                    shear_lhs_le.append(shear[3])
                    shear_lhs_main.append(shear[4])
                    shear_lhs_te.append(shear[5])
                    shear_front_spar.append(shear[6])
                    shear_back_spar.append(shear[7])

                comp_rhs_le = sum(comp_rhs_le) / len(comp_rhs_le)
                comp_rhs_main = sum(comp_rhs_main) / len(comp_rhs_main)
                comp_rhs_te = sum(comp_rhs_te) / len(comp_rhs_te)
                comp_lhs_le = sum(comp_lhs_le) / len(comp_lhs_le)
                comp_lhs_main = sum(comp_lhs_main) / len(comp_lhs_main)
                comp_lhs_te = sum(comp_lhs_te) / len(comp_lhs_te)
                comp_front_spar = sum(comp_front_spar) / len(comp_front_spar)
                comp_back_spar = sum(comp_back_spar) / len(comp_back_spar)
                
                shear_rhs_le = sum(shear_rhs_le) / len(shear_rhs_le)
                shear_rhs_main = sum(shear_rhs_main) / len(shear_rhs_main)
                shear_rhs_te = sum(shear_rhs_te) / len(shear_rhs_te)
                shear_lhs_le = sum(shear_lhs_le) / len(shear_lhs_le)
                shear_lhs_main = sum(shear_lhs_main) / len(shear_lhs_main)
                shear_lhs_te = sum(shear_lhs_te) / len(shear_lhs_te)
                shear_front_spar = sum(shear_front_spar) / len(shear_front_spar)
                shear_back_spar = sum(shear_back_spar) / len(shear_back_spar)
                
                fracs = []
                fracs.append(comp_rhs_le/shear_rhs_le)
                fracs.append(comp_rhs_main/shear_rhs_main)
                fracs.append(comp_rhs_te/shear_rhs_te)
                fracs.append(comp_lhs_le/shear_lhs_le)
                fracs.append(comp_lhs_main/shear_lhs_main)
                fracs.append(comp_lhs_te/shear_lhs_te)
                fracs.append(comp_front_spar/shear_front_spar)
                fracs.append(comp_back_spar/shear_back_spar)                
            if k == 2:
                for index in xrange(len(fracs)):
                    if abs(fracs[index]) < 0.1:
                        mat_dict[index] = forty_five
                    elif abs(fracs[index]) >= 0.1 and abs(fracs[index]) <= 50:
                        mat_dict[index] = quasi
                    elif abs(fracs[index]) > 50:
                        mat_dict[index] = zero_ninety
                bay_new = self.bay_analysis(mat=mat_dict,n_ply_list = n_ply_list)
            if k == 3:
                was_smaller = [[False] * len(bay_new) for _ in range(len(fracs)) ]

                for runs in range(0,6):
                    for i in xrange(len(bay_new)):
                        # Iterate over the sections (bays)

                        for j in xrange(len(fracs)):
                            # Iterate over the parts in the section

                            x =  bay_new[i].buckling_rf_combined[j] - 1
                            if x > 1.2 and was_smaller[j][i] == False:
                                if n_ply_list[j][i] != 4:
                                    n_ply_list[j][i] = n_ply_list[j][i] - 2
                            elif x < 1:
                                if n_ply_list[j][i] != 20:
                                    n_ply_list[j][i] = n_ply_list[j][i] + 2
                                    was_smaller[j][i] = True
                    bay_new = self.bay_analysis(mat=mat_dict,n_ply_list = n_ply_list)


                            

        return bay_new, mat_dict


    @Attribute
    def color_list(self):
        color_rhs_LE = ["YELLOW"]*(len(self.bays)+1)
        color_rhs_main = ["YELLOW"]*(len(self.bays)+1)
        color_rhs_TE = ["YELLOW"]*(len(self.bays)+1)
        color_lhs_LE = ["YELLOW"]*(len(self.bays)+1)
        color_lhs_main = ["YELLOW"]*(len(self.bays)+1)
        color_lhs_TE = ["YELLOW"]*(len(self.bays)+1)
        color_front_spar = ["YELLOW"]*(len(self.bays)+1)
        color_back_spar = ["YELLOW"]*(len(self.bays)+1)
        array = [color_rhs_LE, color_rhs_main, color_rhs_TE, color_lhs_LE, color_lhs_main, color_lhs_TE, color_front_spar,color_back_spar]
        for i in xrange(len(self.optimise_material[0])):
            for j in xrange(len(array)):
                x =  self.optimise_material[0][i].buckling_rf_combined[j] -1
                if x < 1:
                    array[j][i+1] = "RED"
                elif x >= 1 and x <= 1.2:
                        array[j][i+1] = "GREEN"
                elif x > 1.2:
                    array[j][i+1] = "BLUE"
                else:
                    array[j][i+1] = "YELLOW"


        return array

    @Attribute
    def split_faces(self):
        facelist = []
        list = []
        for i in self.rhs_skin_faces():
            facelist.append(i)
        for i in self.lhs_skin_faces():
            facelist.append(i)
        for i in self.spar_faces():
            facelist.append(i)
        for i in xrange(len(facelist)):
            list.append(SplitSurface(built_from= facelist[i], tool = self.bays, colors = self.color_list[i]))
        return list

    @Attribute
    def show_split_faces(self):
        list = []
        for i in xrange(len(self.split_faces)):
            list.append(self.split_faces[i].faces)
        return list


    @Part(in_tree=False)
    def fuse_fuselage(self):
        """
        Fuses together the solids of the fuselage
        :rtype: FusedSolid
        """
        return FusedSolid(shape_in=self.fuselage_part.fuselage_assembly[1],
                          tool=[self.fuselage_part.fuselage_assembly[0], self.fuselage_part.fuselage_assembly[2]])

    @Part(in_tree=False)
    def wet_wings_left(self):
        return SubtractedSolid(shape_in=self.main_wing[0],
                               tool = self.fuse_fuselage)
    @Part(in_tree=False)
    def wet_wings_right(self):
        return SubtractedSolid(shape_in=self.main_wing[1],
                               tool = self.fuse_fuselage)


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
        return STEPWriter(nodes=self.rudder_nodes(),
                          default_directory='../output/CAD')
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
        return STEPWriter(nodes=self.wetted_nodes(),
                          default_directory='../output/CAD')
    @Attribute
    def wetted_area(self):
        main_wings = 2 * (self.wet_wings_left.faces[0].area + self.wet_wings_left.faces[1].area)
        h_t_p = (2 * (self.translate_h_tail_wing[0].faces[0].area + self.translate_h_tail_wing[0].faces[2].area)
                 - (self.fixed_v_wing[1].faces[0].area + self.fixed_v_wing[1].faces[3].area))
        v_t_p = (self.fixed_v_wing[1].area - ((self.fixed_v_wing[1].faces[0].area + self.fixed_v_wing[1].faces[3].area)
                                              + self.fixed_v_wing[1].faces[11].area + self.fixed_v_wing[1].faces[9].area)
                 + self.fixed_v_wing[0].area)
        fuselage = (self.fuse_fuselage.area - (self.fixed_v_wing[1].faces[11].area + self.fixed_v_wing[1].faces[9].area)
                    - 2*self.wet_wings_left.faces[2].area)
        return main_wings+h_t_p+v_t_p+fuselage

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
