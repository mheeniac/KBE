import csv_handle as csvr
import csv


def save_sum(main, htp, vtp, fuse, self):
    """ Saves the variables of current settings to an output file
    :rtype: string and csv
    """
    path = csvr.generate_sum_path("summary.csv")
    first_row = True
    target = main
    with open(path[0], 'rb') as file:  # Open file
        reader = csv.reader(file, delimiter=',', quotechar='|')  # Read into reader and section rows and columns
        with open(path[1], 'wb') as outfile:
            filewriter = csv.writer(outfile, dialect='excel')
            for row in reader:
                if first_row == True:
                    filewriter.writerow(row)
                    first_row = False
                elif '//' in str(row[0]):
                    filewriter.writerow(row)
                    if 'HTP' in str(row[3]):
                        target = htp
                    elif 'VTP' in str(row[3]):
                        target = vtp
                    elif 'MAIN' in str(row[3]):
                        target = main
                    elif 'FUSELAGE' in str(row[3]):
                        target = fuse
                    elif 'CONSTANTS' in str(row[3]):
                        target = self
                    elif 'COMPUTER' in str(row[3]):
                        target = self
                elif row[0] == '':
                    filewriter.writerow(row)
                elif '//' not in str(row[0]):
                    if row[0] == 'Actuator Force':
                        var_name = 'actuator_forces'
                        value = getattr(target,var_name)
                        row[1] = "[" + str(round(value[0][0],1)) + " ; " + str(round(value[0][1],1)) + "]"
                        filewriter.writerow(row)
                    elif row[0] == 'Hinge Forces':
                        var_name = 'total_hinge_force'
                        value = getattr(target, var_name)
                        run = 1
                        for items in value[0]:
                            if run == 1:
                                row[1] = str(round(items,1))
                                run = 2
                            else:
                                row[0] = ''
                                row[1] = str(round(items, 1))
                                row[3] = ''
                            filewriter.writerow(row)
                    elif row[0] == 'Hinge Masses':
                        var_name = 'hinge_mass'
                        value = getattr(target, var_name)
                        run = 1
                        for items in value[0]:
                            if run == 1:
                                row[1] = str(round(items,3))
                                run = 2
                            else:
                                row[0] = ''
                                row[1] = str(round(items, 3))
                                row[3] = ''
                            filewriter.writerow(row)
                    elif row[0] == 'Wetted Area':
                        var_name = 'wetted_area'
                        value = getattr(target, var_name)
                        index = 0
                        row[0] = " \\ \\ " + row[0]
                        filewriter.writerow(row)
                        names = ['Main Wings', 'HTP', 'VTP', 'Fuselage']
                        for items in value:
                            row[2] = "[m^2]"
                            row[0] = names[index]
                            row[3] = ''
                            row[1] = str(round(items, 3))
                            index = index + 1
                            filewriter.writerow(row)
                    elif row[0] == "Main Wing":
                        row[0] = " \\ \\ " + row[0]
                        filewriter.writerow(row)
                        index = 0
                        names = ['Sweep Angle', 'Taper Ratio', 'Dihedral Angle']
                        var_name = ['sweep_angle', 'taper_ratio', 'dihedral_angle']
                        for vars in var_name:
                            value = getattr(self.obj_main_wing.obj_wingset, vars)
                            row[0] = names[index]
                            row[1] = round(value,2)
                            index = index + 1
                            filewriter.writerow(row)
                    elif row[0] == "Horizontal Wing":
                        row[0] = " \\ \\ " + row[0]
                        filewriter.writerow(row)
                        index = 0
                        names = ['Sweep Angle', 'Taper Ratio', 'Dihedral Angle']
                        var_name = ['sweep_angle', 'taper_ratio', 'dihedral_angle']
                        for vars in var_name:
                            value = getattr(self.def_h_tail_wing.obj_wingset, vars)
                            row[0] = names[index]
                            row[1] = round(value, 2)
                            index = index + 1
                            filewriter.writerow(row)
                    else:
                        # Find the name of the variable that we want to request and save
                        var_name = row[0]
                        value = getattr(target, var_name)
                        # Update the value in row
                        row[1] = value
                        # Write the row to a new file
                        filewriter.writerow(row)

    return 'Saved'
