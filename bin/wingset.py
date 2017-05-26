from math import *

from parapy.core import *
from parapy.geom import *
from wing import Wing


# TODO:
# Wing on right place
#
#



class Wingset(GeomBase):
    # This class creates a set of wings that can be used for the main wings or horizontal tail of a plane

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
    airfoil_root = Input('airfoil.dat')

    #: the name of the tip airfoil file
    #: :type: string
    airfoil_tip = Input('airfoil.dat')

    # Label for the tree
    label = 'Wing Set'

    @Part(in_tree=False)
    # object of class wing using local input
    def obj_wingset(self):
        return Wing(w_c_root=self.w_c_root,
                    dihedral_angle_user=self.dihedral_angle_user,
                    w_span=self.w_span,
                    taper_ratio_user=self.taper_ratio_user,
                    TechFactor=self.TechFactor,
                    m_cruise=self.m_cruise,
                    sweep_angle_user=self.sweep_angle_user,
                    airfoil_root=self.airfoil_root,
                    airfoil_tip=self.airfoil_tip)

    @Part(in_tree=False)
    # mirror the part to create a second wing
    def mirror_main_wing(self):
        return MirroredShape(shape_in=self.obj_wingset.wing_part,
                             reference_point=Point(0, 0, 0),
                             vector1=Vector(1, 0, 0),
                             vector2=Vector(0, 1, 0),
                             label='Left Wing')

    @Attribute(in_tree=True)
    def wingset(self):
        """ collects both wings and packs them together into wingset attribute
        :rtype: Part
        """
        return self.mirror_main_wing, self.obj_wingset.wing_part

    @Attribute(in_tree=False)
    def mac_def(self):
        """ This attribute calculates the x-locaiton, y-location and length of the mean aerodynamic chord
        :rtype: collections.Sequence[float]
        """
        sweep = radians(self.obj_wingset.sweep_angle)   # working variable of sweep angle (radians)
        taper = self.obj_wingset.taper_ratio            # working variable for the taper ratio of the wing
        span = self.w_span                              # working variable for the span of a single wing half
        cr = self.w_c_root                              # working variable for the root chord length of the wings

        y_loc = (2 * span / 6) * ((1 + 2 * taper) / (1 + taper))
        x_loc = y_loc / tan((0.5 * pi) - sweep)
        length = (2 * cr / 3) * ((1 + taper + taper ** 2) / (1 + taper))
        return [x_loc, y_loc, length]

    @Attribute(in_tree=False)
    def ref_area(self):
        """ This attribute calculates the reference area of the wingset
        :rtype: float
        """
        return (self.w_c_root + self.obj_wingset.w_c_tip) * self.w_span


if __name__ == '__main__':
    from parapy.gui import display

    obj = Wingset()
    display(obj)
