import csv_handle as csvr
from math import *
from parapy.geom import *
import warnings
from csv_in_out import *

# TODO:
# Output/Input handling

# Return the path of the current directory
DIR = os.path.dirname(__file__)


# Test push and commit
class Fuselage(GeomBase):
    variables = csvr.read_input("fuselage.csv")  # Fuselage Settings

    #: cabin diameter [m]
    #: :type: float
    cabin_diameter = Input(variables["cabin_diameter"])

    #: cabin length [m]
    #: :type: float
    cabin_length = Input(variables["cabin_length"])

    #: fuselage nose slenderness (length over base diameter) [ratio]
    #: :type: float
    nose_slenderness = Input(variables["nose_slenderness"])  # typical value between 1.2 and 2.5

    #: fuselage tailcone slenderness (length of base diameter) [ratio]
    #: :type: float
    tail_slenderness = Input(variables["tail_slenderness"])  # typical between 2.5 - 5

    #: tailcone upsweep angle [degrees]
    #: :type: float
    upsweep_angle = Input(variables["upsweep_angle"])  # typical value between 6  and 11

    #: The taper of the tail section (tip over base) [ratio]
    #: :type: float
    tail_taper = Input(variables["tail_taper"])

    #: number circular of sections that make up the nose []
    #: :type: integer
    n_section = Input(variables["n_section"])

    label = 'Fuselage'

    @Attribute
    def upsweep_angle_func(self):
        """
        This attribute is used to check if the upsweep angle is not too large (tail is not pointing upwards)
        :rtype: float
        """
        angle = self.upsweep_angle
        radius = (self.cabin_diameter / 2) * self.tail_taper  # Radius of the outer tail circle
        max_height = self.cabin_diameter / 2 - radius  # The maximum height possible
        max_angle = degrees(atan(max_height / self.length_tail))  # The angle corresponding to this height
        if angle > max_angle:
            # The angle is not possible, warn and set to max angle
            warn_str = "Upsweep angle too large, max is: {0}".format(max_angle)
            warnings.warn(warn_str)
            return max_angle
        else:
            # All is fine
            return angle

    @Attribute
    def fuselage_length(self):
        """ This computes the total length of the fuselage (tail + cabin + nose)

        :rtype: float
        """
        length = self.length_nose + self.length_tail + self.cabin_length
        label = 'Fuselage Length'
        # input total length
        return length

    @Attribute
    def length_nose(self):
        """ This computes the length of the nose section (slenderness value times the diameter of the cabin)

        :rtype: float
        """
        length = self.nose_slenderness * self.cabin_diameter
        return length

    @Attribute
    def length_tail(self):
        """ This computes the length of the tail section (slenderness value times the diameter of the cabin)

        :rtype: float
        """
        length = self.cabin_diameter * self.tail_slenderness
        return length

    @Attribute
    def fineness_ratio(self):
        """ Computes the fineness ratio of the aircraft. This value is not used for any further calculations but
        merely functions as an output parameter for the user to compare to desired values/literature

        :rtype: float
        """
        return self.fuselage_length / self.cabin_diameter

    @Attribute
    def nose_sections(self):
        """ Creates a function to compute the diameter of the nose sections

        :rtype: collections.Sequence[float]
        """
        array = []  # Initialize empty array
        power = 3.  # The power of the hyperbola  
        for x in range(0, int(100 ** power / (100 ** power / self.n_section) + 1)):
            y = pow(((100 ** power / self.n_section) * x), (1 / power))
            array.append(y)
        return array

    @Attribute
    def position_sections(self):
        """ Generates a position list for the circular sections of the fuselage nose

        :rtype: collections.Sequence[float]
        """
        posList = []  # Initialize empty array
        prev = None  # Set previous to none
        for i in xrange(len(self.nose_sections)):
            if i == 0:
                # Position the first (tip of nose)
                pos = rotate(self.position, Vector(0, 1, 0), radians(90))  # Rotate such that 'z' is lengthwise
            else:
                # Position all the other sections
                pos = translate(prev,
                                'z', self.length_nose / len(self.nose_sections),  # Lengthwise
                                'x', (self.nose_sections[i] * self.cabin_diameter / 200 - self.nose_sections[
                        i - 1] * self.cabin_diameter / 200))  # Making sure the bottom if the nose is flat

            posList.append(pos)  # write current position to the posList
            prev = pos  # Save the precious position
        return posList

    @Part(in_tree=False)
    def nose_circles(self):
        """ Creates the circles for the nose using the diameter list and the position list attributes
            Offsets the height of the first nose section with 0.5 m
        """
        return Circle(radius=self.nose_sections[child.index] * self.cabin_diameter / 200,
                      position=translate(self.position_sections[child.index], 'x', 0.5, ) if child.index == 0 else
                      self.position_sections[child.index],
                      quantify=len(self.nose_sections))

    @Part(in_tree=False)
    def lofted_nose(self):
        """ Creates a lofted surface over the circles of the nose
        """
        return LoftedSolid(self.nose_circles)

    @Part(in_tree=False)
    def cabin_cylinder(self):
        """ Creates a cylinder for the cabin
        """
        return Cylinder(radius=self.cabin_diameter / 2,
                        height=self.cabin_length,
                        position=self.nose_circles[len(self.nose_sections) - 1].position
                        )

    @Attribute
    def tail_x_position(self):
        """ Checks if the user upsweep angle is within a certain limit. Else set it to standard and display warning
            Also calculates the x_position for the fuselage circle centers

        :rtype: float
        """
        if abs(self.upsweep_angle) <= 45:
            x_pos = self.length_tail * tan(radians(self.upsweep_angle_func))
        else:
            warnings.warn("The upsweep angle should be lower than 45! Set to standard 45")
            x_pos = self.length_tail * tan(radians(45))
        return x_pos

    @Part(in_tree=False)
    def tail_circles(self):
        """ Creates the circles for the tail using the taper ratio for the tip diameter and the length of the tail
            for the positioning
        """
        return Circle(radius=[self.cabin_diameter / 2, (self.cabin_diameter / 2) * self.tail_taper][child.index],
                      position=translate(self.cabin_cylinder.edges[0].position,
                                         'x', self.tail_x_position * \
                                         child.index,
                                         'z', self.cabin_length + self.length_tail * child.index),
                      quantify=2)

    @Part(in_tree=False)
    def tail(self):
        """ Lofts the tail cone from the two tail circles
        """
        return LoftedSolid(profiles=self.tail_circles)

    @Attribute
    def fuselage_collection(self):
        """ Collects the three parts to show in the tree
        """
        return self.tail, self.cabin_cylinder, self.lofted_nose

    @Part(in_tree=False)
    def fuse_fuselage(self):
        """ Fuses the fuselage parts into one (used for wetted areas)
        """
        return FusedSolid(shape_in=self.cabin_cylinder,
                          tool=[self.tail, self.lofted_nose])

    @Part
    def fuselage_assembly(self):
        """ Rotate the assembly
        """
        return RotatedShape(shape_in=self.fuselage_collection[child.index],
                            rotation_point=Point(0, 0, 0),
                            vector=Vector(1, 0, 0),  # Rotate such that x is length z is height
                            angle=radians(180),
                            transparency=0.4,
                            quantify=3,
                            label=['Tail', 'Cabin', 'Nose'][child.index],
                            color='White')  # Name in the tree

    @Attribute
    def save_vars(self):
        """ Saves the variables of current settings to an output file

        :rtype: string and csv
        """
        path = csvr.generate_path("fuselage.csv")
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

    obj = Fuselage()
    display(obj)
