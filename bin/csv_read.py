import glob
import os
import csv
from parapy.core import *

class ReadMaterial(Base):
    """
    This class generates an object with a read attribute that will output a the dictionary of a certain material csv file
    It contains all the number of plies and can be accessed through <dict_name>["<nr_plies>"]["<Property>"]
    """
    ply_file = Input()
    materials = {}

    @Attribute
    def generate_path(self):
        directory = '../input/materials'
        path = os.path.join(directory, self.ply_file)
        return path

    @Attribute
    def read(self):
        path = self.generate_path
        with open(path, 'rb') as file:
            reader = csv.reader(file, delimiter=',', quotechar='|')
            row_names = next(reader)    # gets the first line
            for row in reader:
                sub_dict = {}
                n_layers = row[0]
                for x in range(0, len(row)):
                    var_name = row_names[x]
                    value = float(row[x])
                    sub_dict[var_name] = value
                self.materials[n_layers] = sub_dict
        return self.materials