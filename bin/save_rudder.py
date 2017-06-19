import csv_handle as csvr
import csv


def save_rud(main, htp, vtp, fuse, self):
    """ Saves the variables of current settings to an output file
    :rtype: string and csv
    """
    path = csvr.generate_rud_path("rudder.csv")
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
                elif row[0] == '':
                    filewriter.writerow(row)
                elif '//' not in str(row[0]):
                    if 'Form' in row[0]:
                        value = sum([self.rudder_weights_obj.weights_seg[1], self.rudder_weights_obj.weights_seg[3]])
                        row[1] = value
                        filewriter.writerow(row)
                    if 'Hinge Ribs' in row[0]:
                        value = self.rudder_weights_obj.weights_seg[2]
                        row[1] = value
                        filewriter.writerow(row)
                    if row[0] == 'Hinges':
                        value = self.hinge_mass[0]
                        row[1] = value
                        filewriter.writerow(row)
                    # if 'Front Spar' in row[0]:
                    #     filewriter.writerow(row)
                    #     front = self.rudder_weights_obj.weights_seg[4][6]
                    #     index = 1
                    #     for items in front:
                    #         row[0] = 'Bay nr.' + str(index)
                    #         row[1] = items
                    #         filewriter.writerow(row)
                    #         index = index + 1
                    # if 'Back Spar' in row[0]:
                    #     filewriter.writerow(row)
                    #     front = self.rudder_weights_obj.weights_seg[4][7]
                    #     index = 1
                    #     for items in front:
                    #         row[0] = 'Bay nr.' + str(index)
                    #         row[1] = items
                    #         filewriter.writerow(row)
                    #         index = index + 1




    return 'Saved'
