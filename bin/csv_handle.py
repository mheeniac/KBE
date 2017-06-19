import os
import csv
import re


def generate_path(file_name):
    """ This attributed stitches together the file name and the file directory to get the path for the input file
    :rtype: str
    """
    in_dir = '../input'
    out_dir = '../output'
    in_path = os.path.join(in_dir, file_name)
    out_path = os.path.join(out_dir, file_name)
    return in_path, out_path

def generate_sum_path(file_name):
    """ This attributed stitches together the file name and the file directory to get the path for the input file
    :rtype: str
    """
    out_dir = '../output'
    in_path = 'summary_template.csv'
    out_path = os.path.join(out_dir, file_name)
    return in_path, out_path


def read_input(file_name):
    """ This reads the CSV file. Skips the first row (contains no useful information). Then determines if it should
        be a string or a float. Then generates a dictionary item out of every row and finally returns it.
    :rtype: dict
    """
    variables = {}
    path = generate_path(file_name)[0]  # Request the path
    with open(path, 'rb') as file:  # Open file
        reader = csv.reader(file, delimiter=',', quotechar='|')  # Read into reader and section rows and collumns
        next(reader)  # Skip the first line
        for row in reader:  # Iterate over every row
            var_name = row[0]  # Extract the variable name
            if re.search('[a-zA-Z]', row[1]):  # Check if the value column has a letter in it
                value = str(row[1])  # Has letter so convert to string
            else:
                value = float(row[1])  # Has no letter so convert to float
            variables[var_name] = value  # Add to dictionary
    return variables
