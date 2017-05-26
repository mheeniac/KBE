import json
from parapy.core import *
from parapy.geom import *
from csv_in_out import *

class Boxy(GeomBase):
    # Read function from external file
    read = ReadInput(file_name='box.csv')
    # Create dict
    variables = read.read_input

    # Set the editable variables
    width = Input(variables["width"])
    height = Input(variables["height"])
    length = Input(variables["length"])

    @Part
    # Create the geometry
    def box1(self):
        return Box(width=self.width,
                   height=self.height,
                   length=self.length)


    @Attribute
    def save_vars(self):
        path = self.read.generate_path
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

                        value = getattr(self,var_name)
                        # Update the value in row
                        row[1] = value
                        # Write the row to a new file
                        filewriter.writerow(row)
        return 'Saved'


if __name__ == '__main__':
    from parapy.gui import display

    obj = Boxy()
    display(obj)