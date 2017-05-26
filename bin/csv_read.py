import glob
import os
import csv
from parapy.core import *

class ReadMaterial(Base):
    ply_file = Input() 
    n_layers = Input()
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
            n_layers = self.n_layers    # Sets the number of layers
            for row in reader:
                if row[0] == str(n_layers):
                    print row
                    for x in range(0, len(row)):
                        var_name = row_names[x]
                        value = float(row[x])
                        self.materials[var_name] = value
        return self.materials