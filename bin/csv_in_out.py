import glob
import os
import csv
import re


from parapy.core import *
from parapy.geom import GeomBase

class ReadInput(GeomBase):
    #: Name of the csv file to be read
    #: :type: str
    file_name = Input()
    dict_name = Input()

    variables = {}  # Creating empty dictionary to be filled and returned
    variables.clear()

    @Attribute
    def generate_path(self):
        """ This attributed stitches together the file name and the file directory to get the path for the input file

        :rtype: str
        """
        in_dir = '../input'
        out_dir = '../output'
        in_path = os.path.join(in_dir, self.file_name)
        out_path = os.path.join(out_dir, self.file_name)
        return in_path, out_path

    @Attribute
    def read_input(self):
        """ This reads the CSV file. Skips the first row (contains no useful information). Then determines if it should
            be a string or a float. Then generates a dictionary item out of every row and finally returns it.

        :rtype: dict
        """
        self.variables.clear()
        path = self.generate_path[0]  # Request the path
        with open(path, 'rb') as file:  # Open file
            reader = csv.reader(file, delimiter=',', quotechar='|')  # Read into reader and section rows and collumns
            next(reader)  # Skip the first line
            for row in reader:  # Iterate over every row
                var_name = row[0]  # Extract the variable name
                if re.search('[a-zA-Z]', row[1]):  # Check if the value column has a letter in it
                    value = str(row[1])  # Has letter so convert to string
                else:
                    value = float(row[1])  # Has no letter so convert to float
                self.variables[var_name] = value  # Add to dictionary
        return self.variables


