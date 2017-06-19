from bay_analysis_tool.bay_analysis import BayAnalysis
from material_allocation import *
from shear_bend import *

class BayAna(Base):
    craft = Input()
    
    @Attribute
    def force_lines(self):
        """
        Creates the force_lines
        :rtype: object
        """
        return ForceLines(craft=self.craft)
    
    
    def sorted_ribs(self):
        """
        Sorts the ribs
        :rtype: list
        """
        return sorted(self.craft.def_v_tail_wing.rudder_ribs, key=lambda face: face.cog.z)
    
    
    @Attribute
    def bays(self):
        """
        Creates the bay planes
        :rtype: list
        """
        list = []
        list.append(TranslatedPlane(built_from=self.craft.def_v_tail_wing.closure_ribs[0].u_reversed,
                                    displacement=Vector(0, 0, 0.01)))
        for i in xrange(len(self.sorted_ribs())):
            list.append(self.sorted_ribs()[i].u_reversed)
        list.append(TranslatedPlane(built_from=self.craft.def_v_tail_wing.closure_ribs[1].u_reversed,
                                    displacement=Vector(0, 0, -0.01)))
        return list
    
    
    @Attribute
    def positions_planes(self):
        """
        Returns the bay planes z positions
        :rtype: list
        """
        list = []
        dx = self.craft.dx
        for i in xrange(len(self.bays)):
            list.append(
                int((self.bays[i].uv_center_point.z - self.craft.def_v_tail_wing.closure_ribs[0].vertices[0].point.z) / dx))
    
        return list

    def lhs_skin_faces(self):
        """
        Left hand side skin faces
        :rtype: list
        """
        return [self.craft.def_v_tail_wing.fused_le_skin_right, self.craft.def_v_tail_wing.main_skin_right.faces[0],
                self.craft.def_v_tail_wing.te_skin_right.faces[0]]
    
    
    def rhs_skin_faces(self):
        """
        Right hand side skin faces
        :rtype: list
        """
        return [self.craft.def_v_tail_wing.fused_le_skin_left, self.craft.def_v_tail_wing.main_skin_left.faces[0],
                self.craft.def_v_tail_wing.te_skin_left.faces[0]]
    
    
    def spar_faces(self):
        """
        Front and back spar faces
        :rtype: list
        """
        return [self.craft.def_v_tail_wing.rudder_front_spar.faces[0], self.craft.def_v_tail_wing.rudder_back_spar.faces[0]]
    
    
    @Input(settable=True)
    def n_ply_list(self):
        """
        Will give the default ply list
        :rtype: list
        """
        length = len(self.bays) - 1
        n_ply_rhs_LE = [8] * length
        n_ply_rhs_main = [10] * length
        n_ply_rhs_TE = [4] * length
        n_ply_lhs_LE = [8] * length
        n_ply_lhs_main = [10] * length
        n_ply_lhs_TE = [4] * length
        n_ply_front_spar = [8] * length
        n_ply_back_spar = [8] * length
        return n_ply_rhs_LE, n_ply_rhs_main, n_ply_rhs_TE, n_ply_lhs_LE, n_ply_lhs_main, n_ply_lhs_TE, n_ply_front_spar, n_ply_back_spar
    
    
    @Attribute
    def ref_y(self):
        """
        Calculates the ref y
        :rtype: list
        """
        y = []
        for i in xrange(len(self.bays)):
            ref = self.craft.def_v_tail_wing.hingerib_line.start.y + self.craft.def_v_tail_wing.hingerib_line.direction_vector.y / self.craft.def_v_tail_wing.hingerib_line.direction_vector.z * (
            self.craft.def_v_tail_wing.hingerib_line.start.z - self.bays[i].uv_center_point.z)
            y.append(ref)
        return y
    
    
    def bay_analysis(self, mat, n_ply_list):
        """
        Computes the bay analysis
        :rtype: object
        """
        analysis = []
        for i in xrange(len(self.bays) - 1):
            analysis.append(BayAnalysis(Vx=[self.force_lines.force_lines[0][self.positions_planes[i]],
                                            self.force_lines.force_lines[0][self.positions_planes[i + 1]]],
                                        Vy=[self.force_lines.force_lines[1][self.positions_planes[i]],
                                            self.force_lines.force_lines[1][self.positions_planes[i + 1]]],
                                        Mx=[self.force_lines.force_lines[2][self.positions_planes[i]],
                                            self.force_lines.force_lines[2][self.positions_planes[i + 1]]],
                                        My=[self.force_lines.force_lines[3][self.positions_planes[i]],
                                            self.force_lines.force_lines[3][self.positions_planes[i + 1]]],
                                        Mt=[self.force_lines.force_lines[4][self.positions_planes[i]],
                                            self.force_lines.force_lines[4][self.positions_planes[i + 1]]],
                                        ref_x=[self.craft.def_v_tail_wing.d_hinge] * 2,
                                        ref_y=[self.ref_y[i], self.ref_y[i + 1]],
                                        bay_planes=[self.bays[i], self.bays[i + 1]],
                                        rhs_skin_faces=self.rhs_skin_faces(),
                                        lhs_skin_faces=self.lhs_skin_faces(),
                                        spar_faces=self.spar_faces(),
                                        rhs_skin_materials_t=[mat[0][str(n_ply_list[0][i])]['t'],
                                                              mat[1][str(n_ply_list[1][i])]['t'],
                                                              mat[2][str(n_ply_list[2][i])]['t']],
                                        lhs_skin_materials_t=[mat[3][str(n_ply_list[3][i])]['t'],
                                                              mat[4][str(n_ply_list[4][i])]['t'],
                                                              mat[5][str(n_ply_list[5][i])]['t']],
                                        spar_materials_t=[mat[6][str(n_ply_list[6][i])]['t'],
                                                          mat[7][str(n_ply_list[7][i])]['t']],
                                        rhs_skin_materials_E=[mat[0][str(n_ply_list[0][i])]['E'],
                                                              mat[1][str(n_ply_list[1][i])]['E'],
                                                              mat[2][str(n_ply_list[2][i])]['E']],
                                        lhs_skin_materials_E=[mat[3][str(n_ply_list[3][i])]['E'],
                                                              mat[4][str(n_ply_list[4][i])]['E'],
                                                              mat[5][str(n_ply_list[5][i])]['E']],
                                        spar_materials_E=[mat[6][str(n_ply_list[6][i])]['E'],
                                                          mat[7][str(n_ply_list[7][i])]['E']],
                                        rhs_skin_materials_G=[mat[0][str(n_ply_list[0][i])]['G'],
                                                              mat[1][str(n_ply_list[1][i])]['G'],
                                                              mat[2][str(n_ply_list[2][i])]['G']],
                                        lhs_skin_materials_G=[mat[3][str(n_ply_list[3][i])]['G'],
                                                              mat[4][str(n_ply_list[4][i])]['G'],
                                                              mat[5][str(n_ply_list[5][i])]['G']],
                                        spar_materials_G=[mat[6][str(n_ply_list[6][i])]['G'],
                                                          mat[7][str(n_ply_list[7][i])]['G']],
                                        rhs_skin_materials_D=[
                                            [mat[0][str(n_ply_list[0][i])]['D11'], mat[0][str(n_ply_list[0][i])]['D22'],
                                             mat[0][str(n_ply_list[0][i])]['D22'], mat[0][str(n_ply_list[0][i])]['D12']],
                                            [mat[1][str(n_ply_list[1][i])]['D11'], mat[1][str(n_ply_list[1][i])]['D22'],
                                             mat[1][str(n_ply_list[1][i])]['D22'], mat[1][str(n_ply_list[1][i])]['D12']],
                                            [mat[2][str(n_ply_list[2][i])]['D11'], mat[2][str(n_ply_list[2][i])]['D22'],
                                             mat[2][str(n_ply_list[2][i])]['D22'], mat[2][str(n_ply_list[2][i])]['D12']]],
                                        lhs_skin_materials_D=[
                                            [mat[3][str(n_ply_list[3][i])]['D11'], mat[3][str(n_ply_list[3][i])]['D22'],
                                             mat[3][str(n_ply_list[3][i])]['D22'], mat[3][str(n_ply_list[3][i])]['D12']],
                                            [mat[1][str(n_ply_list[4][i])]['D11'], mat[1][str(n_ply_list[4][i])]['D22'],
                                             mat[1][str(n_ply_list[4][i])]['D22'], mat[1][str(n_ply_list[4][i])]['D12']],
                                            [mat[5][str(n_ply_list[5][i])]['D11'], mat[5][str(n_ply_list[5][i])]['D22'],
                                             mat[5][str(n_ply_list[5][i])]['D22'], mat[5][str(n_ply_list[5][i])]['D12']]],
                                        spar_materials_D=[
                                            [mat[6][str(n_ply_list[6][i])]['D11'], mat[6][str(n_ply_list[6][i])]['D22'],
                                             mat[6][str(n_ply_list[6][i])]['D22'], mat[6][str(n_ply_list[6][i])]['D12']],
                                            [mat[7][str(n_ply_list[7][i])]['D11'], mat[7][str(n_ply_list[7][i])]['D22'],
                                             mat[7][str(n_ply_list[7][i])]['D22'], mat[7][str(n_ply_list[7][i])]['D12']]],
                                        N=3))
        return analysis
    
    
    @Attribute
    def optimise_material(self):
        """
        Optimisation of the used material
        :rtype: list
        """
        # Defines material
        quasi = ReadMaterial(ply_file="quasi_isotropic.csv").read
        forty_five = ReadMaterial(ply_file="forty_five.csv").read
        zero_ninety = ReadMaterial(ply_file="zero_ninety.csv").read
    
        if self.craft.override == True:
            p = 3
        else:
            p = 4
    
        for k in range(1, p):
            if k == 1:
                # Defines default material
                mat_dict = [0] * 8
                mat_dict[0] = forty_five
                mat_dict[1] = forty_five
                mat_dict[2] = forty_five
                mat_dict[3] = forty_five
                mat_dict[4] = forty_five
                mat_dict[5] = forty_five
                mat_dict[6] = forty_five
                mat_dict[7] = forty_five
                # Defines default number of plies
                n_ply_list = self.n_ply_list
                # Runs bay analysis
                bay = self.bay_analysis(mat=mat_dict, n_ply_list=n_ply_list)
    
                # Creates arrays
                comp_rhs_le = []
                comp_rhs_main = []
                comp_rhs_te = []
                comp_lhs_le = []
                comp_lhs_main = []
                comp_lhs_te = []
                comp_front_spar = []
                comp_back_spar = []
    
                # Creates arrays
                shear_rhs_le = []
                shear_rhs_main = []
                shear_rhs_te = []
                shear_lhs_le = []
                shear_lhs_main = []
                shear_lhs_te = []
                shear_front_spar = []
                shear_back_spar = []
    
                # Look if it mainly under compression or shear or both
                for sections in bay:
                    comp = sections.max_compression_lst
                    shear = sections.max_shear_lst
                    comp_rhs_le.append(comp[0])
                    comp_rhs_main.append(comp[1])
                    comp_rhs_te.append(comp[2])
                    comp_lhs_le.append(comp[3])
                    comp_lhs_main.append(comp[4])
                    comp_lhs_te.append(comp[5])
                    comp_front_spar.append(comp[6])
                    comp_back_spar.append(comp[7])
    
                    shear_rhs_le.append(shear[0])
                    shear_rhs_main.append(shear[1])
                    shear_rhs_te.append(shear[2])
                    shear_lhs_le.append(shear[3])
                    shear_lhs_main.append(shear[4])
                    shear_lhs_te.append(shear[5])
                    shear_front_spar.append(shear[6])
                    shear_back_spar.append(shear[7])
    
                comp_rhs_le = sum(comp_rhs_le) / len(comp_rhs_le)
                comp_rhs_main = sum(comp_rhs_main) / len(comp_rhs_main)
                comp_rhs_te = sum(comp_rhs_te) / len(comp_rhs_te)
                comp_lhs_le = sum(comp_lhs_le) / len(comp_lhs_le)
                comp_lhs_main = sum(comp_lhs_main) / len(comp_lhs_main)
                comp_lhs_te = sum(comp_lhs_te) / len(comp_lhs_te)
                comp_front_spar = sum(comp_front_spar) / len(comp_front_spar)
                comp_back_spar = sum(comp_back_spar) / len(comp_back_spar)
    
                shear_rhs_le = sum(shear_rhs_le) / len(shear_rhs_le)
                shear_rhs_main = sum(shear_rhs_main) / len(shear_rhs_main)
                shear_rhs_te = sum(shear_rhs_te) / len(shear_rhs_te)
                shear_lhs_le = sum(shear_lhs_le) / len(shear_lhs_le)
                shear_lhs_main = sum(shear_lhs_main) / len(shear_lhs_main)
                shear_lhs_te = sum(shear_lhs_te) / len(shear_lhs_te)
                shear_front_spar = sum(shear_front_spar) / len(shear_front_spar)
                shear_back_spar = sum(shear_back_spar) / len(shear_back_spar)
    
                fracs = []
                fracs.append(comp_rhs_le / shear_rhs_le)
                fracs.append(comp_rhs_main / shear_rhs_main)
                fracs.append(comp_rhs_te / shear_rhs_te)
                fracs.append(comp_lhs_le / shear_lhs_le)
                fracs.append(comp_lhs_main / shear_lhs_main)
                fracs.append(comp_lhs_te / shear_lhs_te)
                fracs.append(comp_front_spar / shear_front_spar)
                fracs.append(comp_back_spar / shear_back_spar)
            if k == 2:
                # Allocated new material
                for index in xrange(len(fracs)):
                    if abs(fracs[index]) < 0.1:
                        mat_dict[index] = forty_five
                    elif abs(fracs[index]) >= 0.1 and abs(fracs[index]) <= 50:
                        mat_dict[index] = quasi
                    elif abs(fracs[index]) > 50:
                        mat_dict[index] = zero_ninety
                # Compute a new bay analysis
                bay_new = self.bay_analysis(mat=mat_dict, n_ply_list=n_ply_list)
            if k == 3:
                # Optimisation of the number of plies
                was_smaller = [[False] * len(bay_new) for _ in range(len(fracs))]
                for runs in range(0, 6):
                    for i in xrange(len(bay_new)):
                        # Iterate over the sections (bays)
                        for j in xrange(len(fracs)):
                            # Iterate over the parts in the section
                            x = bay_new[i].buckling_rf_combined[j] - 1
                            if x > 1.2 and was_smaller[j][i] == False:
                                if n_ply_list[j][i] != 4:
                                    n_ply_list[j][i] = n_ply_list[j][i] - 2
                            elif x < 1:
                                if n_ply_list[j][i] != 20:
                                    n_ply_list[j][i] = n_ply_list[j][i] + 2
                                    was_smaller[j][i] = True
                    # Compute new bay analysis several times
                    bay_new = self.bay_analysis(mat=mat_dict, n_ply_list=n_ply_list)
        return bay_new, mat_dict
    
    
    @Attribute
    def color_list(self):
        """
        Define the color of the skin faces of the rudder.
        :rtype: list
        """
        color_rhs_LE = ["YELLOW"] * (len(self.bays) + 1)
        color_rhs_main = ["YELLOW"] * (len(self.bays) + 1)
        color_rhs_TE = ["YELLOW"] * (len(self.bays) + 1)
        color_lhs_LE = ["YELLOW"] * (len(self.bays) + 1)
        color_lhs_main = ["YELLOW"] * (len(self.bays) + 1)
        color_lhs_TE = ["YELLOW"] * (len(self.bays) + 1)
        color_front_spar = ["YELLOW"] * (len(self.bays) + 1)
        color_back_spar = ["YELLOW"] * (len(self.bays) + 1)
        array = [color_rhs_LE, color_rhs_main, color_rhs_TE, color_lhs_LE, color_lhs_main, color_lhs_TE, color_front_spar,
                 color_back_spar]
        for i in xrange(len(self.optimise_material[0])):
            for j in xrange(len(array)):
                x = self.optimise_material[0][i].buckling_rf_combined[j] - 1
                if x < 1:
                    array[j][i + 1] = "RED"
                    warnings.warn("A safety margin is too low, check GUI which area is violent")
                elif x >= 1 and x <= 1.2:
                    array[j][i + 1] = "GREEN"
                elif x > 1.2:
                    array[j][i + 1] = "BLUE"
                else:
                    array[j][i + 1] = "YELLOW"
        return array
    
    
    @Attribute
    def split_faces(self):
        """
        Split the colored skin faces of the rudder.
        :rtype: list
        """
        facelist = []
        list = []
        for i in self.rhs_skin_faces():
            facelist.append(i)
        for i in self.lhs_skin_faces():
            facelist.append(i)
        for i in self.spar_faces():
            facelist.append(i)
        for i in xrange(len(facelist)):
            list.append(SplitSurface(built_from=facelist[i], tool=self.bays, colors=self.color_list[i]))
        return list
    
    
    @Attribute
    def show_split_faces(self):
        """
        Shows the colored skin faces of the rudder.
        :rtype: list
        """
        list = []
        for i in xrange(len(self.split_faces)):
            list.append(self.split_faces[i].faces)
        return list