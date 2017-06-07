from math import *
import os
from parapy.core import *
from parapy.geom import *
import warnings


# TODO:
#
#
#

class Wing(GeomBase):
    # This class creates a single wing part

    #: length of the root chord [m]
    #: :type: float
    w_c_root = Input(3)

    #: single wing span [m]
    #: :type: float
    w_span = Input(7)

    #: wing sweep angle [degrees]
    #: :type: float or str
    sweep_angle_user = Input('NaN')  # Overwrites default function if ~= 'NaN'

    #: wing taper ratio []
    #: :type: float or str
    taper_ratio_user = Input('NaN')  # Overwrites the default function if ~= 'NaN'

    #: wing dihedral angle [degrees]
    #: :type: float or str
    dihedral_angle_user = Input('NaN')  # Overwrites the default function if ~= 'NaN'

    #: jet cruise speed [mach]
    #: :type: float
    m_cruise = Input(0.8)  # Used to calculate the default sweep angle

    #: airfoil technology factor []
    #: :type: float
    TechFactor = Input(0.86)  # Technology factor is equal to 0.87 NACA 6 airfoil and 1 to other conventional airfoils

    #: the name of the root airfoil file
    #: :type: string
    airfoil_root=Input('airfoil.dat')

    #: the name of the tip airfoil file
    #: :type: string
    airfoil_tip=Input('airfoil.dat')


    # Label for the tree
    label = 'Wing'

    @Attribute
    def sweep_angle(self):
        """Sweep Angle [degrees] is determined using the technology factor and the cruise speed in Mach.
            Built in check to prevent crash due to too low mach value
        :rtype: float
        """

        if self.sweep_angle_user == 'NaN':  # if not defined, use default formula
            m_min = 0.75*self.TechFactor - 0.03 # Calculate minimum needed cruise speed for acos
            if self.m_cruise >= m_min:
                angle = degrees(acos(0.75 * self.TechFactor / (self.m_cruise + 0.03)))
            elif self.m_cruise < m_min:
                warnings.warn("Cruise speed too low to calculate sweep angle. Set to 0. Minimum cruise speed is:")
                print(m_min)
                angle = 0
        elif abs(self.sweep_angle_user) >= 90:
            warnings.warn("Sweep angle must be lower than 90 degrees, automatically set to 20")
            angle = 20
        else:  # If set by user, use that value for angle
            angle = self.sweep_angle_user

        return angle

    @Attribute
    def w_sweep(self):
        """Calculate the sweep offset for the tip using the sweep angle (based on 1/4 chord), returns [m]
        :rtype: float
        """
        sweep=self.w_span/tan(radians(90-self.sweep_angle))+0.25*(self.w_c_root - self.w_c_tip)

        return sweep

    @Attribute
    def taper_ratio(self):
        """ Check if taper ratio is set by user, otherwise use default formula to calculate taper ratio
        :rtype: float
        """
        if self.taper_ratio_user == 'NaN':  # If not defined, use the following formula
            ratio = 0.2 * (2. - radians(self.sweep_angle))  # formula from reference material
        elif self.taper_ratio_user == 0:    # check to prevent crash for 0
            warnings.warn("Taper ratio must be > 0, automatically set to 0.35")
            ratio = 0.35
        else:  # If set by user, use that value
            ratio = self.taper_ratio_user
        return ratio

    @Attribute
    def aspect_ratio(self):
        """ Calculate the aspect ratio for a trapezoidal reference area. Not used for furhter calculations but
            purely for user.
        :rtype: float
        """
        return 2. * self.w_span/(self.w_c_root*(1. + self.taper_ratio))


    @Attribute
    def dihedral_angle(self):
        """ Check if dihedral angle is set by user, otherwise use default formula to calculate [degrees]
        :rtype: integer
        """
        if self.dihedral_angle_user == 'NaN':           # If not defined, use the following formula
            angle = 3 + 2 - int(self.sweep_angle*0.1)   # formula for bottom wings
        else:
            angle = self.dihedral_angle_user            # Pick user defined value

        return angle

    @Attribute
    def aspect_ratio(self):
        """ Returns the aspect ratio of the wings []
        :rtype: float
        """
        ratio = 2. * self.w_span / (self.w_c_root * (1. + self.taper_ratio))
        return ratio

    @Attribute
    def w_c_tip(self):
        """ calculates the length of the tip chord, using the taper ratio [m]
        :rtype: float
        """
        return self.taper_ratio * self.w_c_root

    @Attribute
    def pts(self):
        """ Extract airfoil coordinates from data file and create a list of
        points for both tip and root

        :rtype: collections.Sequence[Point]
        """
        f_directory='../input/airfoils/'    # relative path location for airfoil database

        with open(os.path.join(f_directory, self.airfoil_root), 'r') as f:  # join directory and file name
            points_root = []    # empty list
            for line in f:      # read line by line
                x, y = line.split(' ', 1)   # x and y separated by space
                # Convert the string to a number and append list
                points_root.append(Point(float(x), float(y)))

        with open(os.path.join(f_directory, self.airfoil_tip), 'r') as f:  # join directory and file name
            points_tip = []     # empty list
            for line in f:      # read line by line
                x, y = line.split(' ', 1)   # x and y separated by space
                # Convert the string to a number and append list
                points_tip.append(Point(float(x), float(y)))

        return points_root , points_tip # Returns root in [0] and tip in [1]

    @Part
    def root_crv(self):
        # A fitted curve around the airfoil data for the Root Chord
        return FittedCurve(self.pts[0], hidden=True)

    @Part
    def tip_crv(self):
        # A fitted curve around the airfoil data for the Tip Chord
        return FittedCurve(self.pts[1], hidden=True)

    @Part
    def scaled_tip(self):
        # Scale the tip curve using the tip chord length
        return ScaledCurve(self.tip_crv, self.tip_crv.position, self.w_c_tip, hidden=True)

    @Part
    def scaled_root(self):
        # Scale the root curve using the root chord length
        return ScaledCurve(self.root_crv, self.root_crv.position, self.w_c_root, hidden=True)

    @Part
    def positioned_tip(self):
        # translate the tip curve to the correct position using the sweep, span and dihedral angle
        return TransformedCurve(self.scaled_tip, self.scaled_tip.position,
                                translate(self.scaled_tip.position,
                                          'z', self.w_span,
                                          'y', 1*self.w_span*sin(radians(self.dihedral_angle)),
                                          'x', self.w_sweep), hidden=True)

    @Part
    def wing_part(self):
        return LoftedSolid([self.scaled_root, self.positioned_tip],
                           label = 'Wing Solid')

    @Attribute
    def mac_y_loc(self):
        """ calculates the lengthwise (y in final aircraft) position of the mean aerodynamic chord

        :rtype: Point
        """
        y_pos = (self.w_span/6)*((1+2*self.taper_ratio**2)/(1+self.taper_ratio))
        return Point(0, y_pos, 0)



if __name__ == '__main__':
    from parapy.gui import display

    obj = Wing()
    display(obj)
