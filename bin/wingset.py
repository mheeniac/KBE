from math import *
import csv_handle as csvr
from parapy.core import *
from parapy.geom import *
from wing import Wing
from csv_in_out import *


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
    sweep_angle = Input('NaN')  # Overwrites default function if ~= 'NaN'

    #: wing taper ratio []
    #: :type: float or str
    taper_ratio = Input('NaN')  # Overwrites the default function if ~= 'NaN'

    #: wing dihedral angle [degrees]
    #: :type: float or str
    dihedral_angle = Input('NaN')  # Overwrites the default function if ~= 'NaN'

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
                    dihedral_angle_user=self.dihedral_angle,
                    w_span=self.w_span,
                    taper_ratio_user=self.taper_ratio,
                    TechFactor=self.TechFactor,
                    m_cruise=self.m_cruise,
                    sweep_angle_user=self.sweep_angle,
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

    @Attribute
    def calc_lowest_point(self):
        """
        This attribute calculates the location of the lowest point on the wing. This will be an offset to be used when
        translating the main wing
        :rtype: float
        """
        lowest_point = 0.
        for points in self.wingset[0].edges[0].sample_points:
            if points[1] >= lowest_point:
                lowest_point = points[1]
        return lowest_point
    @Attribute
    def save_vars(self):
        """ Saves the variables of current settings to an output file

        :rtype: string and csv
        """
        path = csvr.generate_path("mwing.csv")
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

    obj = Wingset()
    display(obj)
