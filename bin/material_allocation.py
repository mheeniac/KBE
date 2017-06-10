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

    @Input
    def n_spar(self):
        """
        The number of plies for the front spar [0] and the back spar [1]
        :rtype: tuple[int]
        """
        if self.is_default:
            return [8, 8]
        else:
            return None

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
        The number of plies for the closure ribs
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

    @Input
    def n_LE(self):
        """
        The number of plies for leading edge of the rudder skin
        :rtype: int
        """
        if self.is_default:
            return 8
        else:
            return None

    @Input
    def n_main(self):
        """
        The number of plies for the main skin of the rudder
        :rtype: int
        """
        if self.is_default:
            return 10
        else:
            return None

    @Input
    def n_TE(self):
        """
        The number of plies for the leading edge skin of the rudder
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
        area_dict["Front Spar"] = self.obj.def_v_tail_wing.rudder_front_spar.area
        area_dict["Back Spar"] = self.obj.def_v_tail_wing.rudder_back_spar.area
        area_dict["Closure Ribs"] = [self.obj.def_v_tail_wing.turned_rudder[22].shape_in.area,
                                     self.obj.def_v_tail_wing.turned_rudder[23].shape_in.area]
        area_dict["Ribs"] = (self.obj.def_v_tail_wing.turned_rudder[1].shape_in.area +
                             self.obj.def_v_tail_wing.turned_rudder[1].shape_in.area) / 2
        area_dict["TE"] = (self.obj.def_v_tail_wing.turned_rudder[0].faces[0].area +
                           self.obj.def_v_tail_wing.turned_rudder[0].faces[1].area +
                           self.obj.def_v_tail_wing.turned_rudder[0].faces[6].area +
                           self.obj.def_v_tail_wing.turned_rudder[0].faces[7].area)
        area_dict["Main"] = (self.obj.def_v_tail_wing.turned_rudder[0].faces[2].area +
                             self.obj.def_v_tail_wing.turned_rudder[0].faces[5].area)
        area_dict["LE"] = (self.obj.def_v_tail_wing.turned_rudder[0].faces[3].area +
                           self.obj.def_v_tail_wing.turned_rudder[0].faces[4].area)
        return area_dict

    @Attribute
    def weights(self):
        areas = self.areas
        quasi = ReadMaterial(ply_file = "quasi_isotropic.csv").read
        forty_five = ReadMaterial(ply_file="forty_five.csv").read
        zero_ninety = ReadMaterial(ply_file="zero_ninety.csv").read
        w_f_s = quasi[str(self.n_spar[0])]["rho"] * areas["Front Spar"]
        w_b_s = quasi[str(self.n_spar[1])]["rho"] * areas["Back Spar"]
        w_c_r = zero_ninety[str(self.n_close_ribs)]["rho"] * (areas["Closure Ribs"][0] + areas["Closure Ribs"][1])
        w_h_r = []
        for nr_plies in self.n_hinge_ribs:
            w_h_r.append(zero_ninety[str(nr_plies)]["rho"] * areas["Ribs"])
        w_h_r = sum(w_h_r)
        w_te = forty_five[str(self.n_TE)]["rho"] * areas["TE"]
        w_le = forty_five[str(self.n_LE)]["rho"] * areas["LE"]
        w_main = forty_five[str(self.n_main)]["rho"] * areas["Main"]
        w_form = self.obj.def_v_tail_wing.formrib_plns.quantify * zero_ninety[str(self.n_form_ribs)]["rho"] * areas["Ribs"]
        total = w_f_s + w_b_s + w_c_r + w_h_r+w_te+w_le+w_main+w_form
        return total

