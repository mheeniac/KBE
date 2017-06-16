from parapy.geom import *
from csv_read import *


class ApplyMat(GeomBase):
    """
    This class applies the materials for each section of the rudder and calculates the weight. There is a default setting
    which can be applied without knowing the moment and shear stresses etc. There is also an optimized version.
    """

    #: Allows the user to say if the default settings should be used or not
    #: :type: bool
    is_default = Input()

    #: The hinge forces
    #: :type: tuple
    hinge_forces = Input()

    #: Reference to self of the aircraft
    obj = Input()

    #: Multi array with the number of plies per segment
    n_plies = Input()

    #: Material dictionary to see which materials are needed
    mat_dict = Input()

    @Input
    def n_close_ribs(self):
        """
        The number of plies for the closure ribs
        :rtype: int
        """
        if self.is_default:
            return 6
        else:
            return None

    @Input
    def n_hinge_ribs(self):
        """
        The number of plies for the hinge ribs
        :rtype: int
        """
        if self.is_default:
            forces = self.hinge_forces
            layers = []
            # Loop over the forces and see if they exceed 60 kN
            for item in forces:
                if item >= 60000:
                    layers.append(6)
                else:
                    layers.append(4)
            return layers
        else:
            return None

    @Input
    def n_form_ribs(self):
        """
        The number of plies for the form ribs
        :rtype: int
        """
        if self.is_default:
            return 4
        else:
            return None

    @Attribute
    def areas(self):
        """
        Create a dictionary that contains the areas of all the relevant parts
        :rtype: dict
        """
        area_dict = {}
        area_dict["Closure Ribs"] = [self.obj.def_v_tail_wing.closure_ribs[0].area,
                                     self.obj.def_v_tail_wing.closure_ribs[1].area]
        area_dict["Ribs"] = (self.obj.def_v_tail_wing.rudder_ribs[0].area +
                             self.obj.def_v_tail_wing.rudder_ribs[len(self.obj.def_v_tail_wing.rudder_ribs)-1].area) / 2
        return area_dict

    @Attribute
    def weights(self):
        areas = self.areas
        bay_weights = []
        quasi = ReadMaterial(ply_file="quasi_isotropic.csv").read
        forty_five = ReadMaterial(ply_file="forty_five.csv").read
        zero_ninety = ReadMaterial(ply_file="zero_ninety.csv").read

        part_in = 0
        for part in self.n_plies:
            index = 1
            for nr in part:
                area = self.obj.split_faces[part_in].faces[index].area
                bay_weights.append(self.mat_dict[part_in][str(nr)]["rho"] * area)
                index = index + 1
            part_in = part_in + 1
        # bay_weights.append(self.mat_dict[0][str(self.n_plies[0][0])]["rho"] * areas["LE"])
        # bay_weights.append(self.mat_dict[3][str(self.n_plies[3][0])]["rho"] * areas["TE"])
        bay_weights = sum(bay_weights)


        w_c_r = zero_ninety[str(self.n_close_ribs)]["rho"] * (areas["Closure Ribs"][0] + areas["Closure Ribs"][1])
        w_h_r = []
        for nr_plies in self.n_hinge_ribs:
            w_h_r.append(zero_ninety[str(nr_plies)]["rho"] * areas["Ribs"])
        w_h_r = sum(w_h_r)
        w_form = self.obj.def_v_tail_wing.formrib_plns.quantify * zero_ninety[str(self.n_form_ribs)]["rho"] * areas[
            "Ribs"]
        total = bay_weights + w_c_r + w_h_r + w_form
        return total
