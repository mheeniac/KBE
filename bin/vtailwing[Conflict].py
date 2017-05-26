from math import *

from parapy.core import *
from parapy.geom import *
from wing import Wing


class VTailWing(Base):
    w_c_root = Input()

    w_c_tip_user = Input()  # Overwrites default function if ~= 'NaN'

    #: wing span [m]
    #: :type: float
    w_span = Input(4.)

    #: wing sweep angle [degrees]
    #: :type: float or str
    sweep_angle_user = Input(0)  # Overwrites default function if ~= 'NaN'

    #: wing taper ratio []
    #: :type: float or str
    taper_ratio = Input('NaN')  # Overwrites the default function if ~= 'NaN'

    #: wing dihedral angle [degrees]
    #: :type: float or str
    dihedral_angle_user = Input(0)  # Overwrites the default function if ~= 'NaN'

    #: jet cruise speed [mach]
    #: :type: float
    m_cruise = Input()  # Used to calculate the default sweep angle

    #: airfoil technology factor []
    #: :type: float
    TechFactor = Input()

    #: the name of the airfoil file of the tip
    #: :type: string
    airfoil_tip = Input('airfoil.dat')

    #: the name of the airfoil file of the root
    #: :type: string
    airfoil_root = Input('airfoil.dat')

    d_hinge = Input(0.5)
    p_zero = Input(0.25)
    p_rib = Input(0.5)
    number_hinges = Input(2)
    dz_root_hinge_rib = Input(0.2)
    dz_tip_hinge_rib = Input(0.2)
    rhl_root = Input(0.05)
    rhl_tip = Input(0.06)

    @Attribute
    def w_c_root(self):
        return (5./4.)*self.w_span

    @Attribute
    def w_c_tip_user(self):
        return (1.5/4)*self.w_span

    @Attribute
    def d_hinge(self):
        return (0.5/4)*self.w_span

    @Attribute
    def r_rudder(self):
        return 0.8*self.p_zero

    @Attribute
    def b_rudder(self):
        return (3./4.)*self.w_span


    @Attribute
    # Converts the tail sweep to 0.25 sweep
    def calc_v_sweep_angle(self):
        if self.sweep_angle_user != 'NaN':
            angle =  atan(0.75*(self.w_c_root-self.w_c_tip_user)/self.w_span) + self.sweep_angle_user
        else:
            angle =  atan(0.75*(self.w_c_root-self.w_c_tip_user)/self.w_span)
        return degrees(angle)

    @Part(in_tree=False)
    def def_vwing(self):
        return Wing(w_c_root=self.w_c_root,
                    w_span=self.w_span,
                    w_c_tip_user=self.w_c_tip_user,
                    sweep_angle_user=self.calc_v_sweep_angle,
                    dihedral_angle_user=self.dihedral_angle_user,
                    TechFactor=self.TechFactor,
                    m_cruise=self.m_cruise,
                    taper_ratio=self.taper_ratio,
                    airfoil_tip=self.airfoil_tip,
                    airfoil_root=self.airfoil_root
                    )

    @Part
    def vwing_oml(self):
        return FusedShell(shape_in=self.def_vwing.sld3.faces[0],
                          tool=[self.def_vwing.sld3.faces[1],self.def_vwing.sld3.faces[2]],
                          )

    @Attribute
    def rudder_pln_locs(self):
        return [Point(self.w_c_root, 0, self.r_rudder), Point(self.w_c_root, 0, self.r_rudder + self.b_rudder)]

    @Part
    def hinge_pln(self):
        return Plane(reference=Point(self.w_c_root - self.d_hinge, 0, 0),
                     normal=Vector(1,
                                   0,
                                   0)
                     )


    @Part
    def rudder_plns(self):
        return Plane(quantify=2,
                     reference=self.rudder_pln_locs[child.index],
                     normal=Vector(0, 0, 1))

    @Part
    def fin_plns(self):
        return Plane(reference=Point(0, 0, self.p_zero + self.p_rib * child.index),
                     normal=Vector(0,
                                   0,
                                   1),
                     quantify=8
                     )

    @Part
    def fused_rudder_and_hinge_plns(self):
        return FusedShell(shape_in=self.vwing_oml,
                          tool= [self.rudder_plns[0],self.rudder_plns[1],self.hinge_pln])

    @Part
    def rudder_plns_fused(self):
        return FusedShell(shape_in=self.vwing_oml,
                          tool=self.rudder_plns)

    @Part
    def fixed_part(self):
        return FusedShell(shape_in=self.fused_rudder_and_hinge_plns.faces[16],
                          tool=  [self.fused_rudder_and_hinge_plns.faces[0],
                                  self.fused_rudder_and_hinge_plns.faces[1],
                                  self.fused_rudder_and_hinge_plns.faces[2],
                                  self.fused_rudder_and_hinge_plns.faces[5],
                                  self.fused_rudder_and_hinge_plns.faces[6],
                                  self.fused_rudder_and_hinge_plns.faces[7],
                                  self.fused_rudder_and_hinge_plns.faces[8],
                                  self.fused_rudder_and_hinge_plns.faces[9],
                                  self.fused_rudder_and_hinge_plns.faces[10],
                                  self.fused_rudder_and_hinge_plns.faces[11],
                                  self.fused_rudder_and_hinge_plns.faces[13],
                                  self.fused_rudder_and_hinge_plns.faces[14],
                                  self.fused_rudder_and_hinge_plns.faces[12],
                                  self.fused_rudder_and_hinge_plns.faces[18],
                                  self.fused_rudder_and_hinge_plns.faces[17],
                                  ]
                          )

    @Part
    def fixed_part_with_ribs(self):
        return FusedShell(shape_in = self.fixed_part,
                   tool= self.fin_plns)

    @Part
    def translate_rudder_closure_ribs_planes(self):
        return TranslatedPlane(built_from=self.rudder_plns[child.index],
                               displacement = Vector(0,0,(1-2*child.index)*0.01),
                               quantify=2)

    @Part
    def rudder_shell_partly(self):
        return FusedShell(shape_in=self.fused_rudder_and_hinge_plns.faces[3],
                          tool= [self.fused_rudder_and_hinge_plns.faces[4],
                                 self.fused_rudder_and_hinge_plns.faces[14],
                                 self.translate_rudder_closure_ribs_planes[0],
                                 self.translate_rudder_closure_ribs_planes[1]
                                 ]
                          )

    @Part
    def rudder_shell(self):
        return FusedShell(shape_in=self.rudder_shell_partly.faces[3],
                          tool= [self.rudder_shell_partly.faces[4],
                                 self.rudder_shell_partly.faces[5],
                                 self.rudder_shell_partly.faces[9],
                                 self.rudder_shell_partly.faces[10]
                                 ]
                          )

    # @Part
    # def hinge_pln(self):
    #     return Plane(reference=Point(self.w_c_root - self.d_hinge, 0, 0),
    #                  normal=Vector(1,
    #                                0,
    #                                0)
    #                  )
    #
    # @Part
    # def hinge_pln_fused(self):
    #     return FusedShell(shape_in=self.vwing_oml,
    #                       tool=self.hinge_pln)
    #
    # @Part
    # def back_shell(self):
    #     return FusedShell(shape_in=self.hinge_pln_fused.faces[0],
    #                       tool=[self.hinge_pln_fused.faces[1],self.hinge_pln_fused.faces[2],self.hinge_pln_fused.faces[3],self.hinge_pln_fused.faces[7]])
    # @Part
    # def front_shell(self):
    #     return FusedShell(shape_in=self.hinge_pln_fused.faces[4],
    #                       tool=[self.hinge_pln_fused.faces[5],self.hinge_pln_fused.faces[6],self.hinge_pln_fused.faces[7]])
    #
    #
    # @Attribute
    # def rudder_pln_locs(self):
    #     return [Point(self.w_c_root, 0, self.r_rudder), Point(self.w_c_root, 0, self.r_rudder + self.b_rudder)]
    #
    # @Part
    # def rudder_plns(self):
    #     return Plane(quantify=2,
    #                  reference=self.rudder_pln_locs[child.index],
    #                  normal=Vector(0, 0, 1))

    # @Part
    # def rudder_plns_fused(self):
    #     return FusedShell(shape_in=self.back_shell,
    #                       tool=self.rudder_plns)
    #
    # @Part
    # def translate_rudder_closure_ribs_planes(self):
    #     return TranslatedPlane(built_from=self.rudder_plns[child.index],
    #                            displacement = Vector(0,0,(1-2*child.index)*0.01),
    #                            quantify=2)
    # @Part
    # def rudder_shell_partly(self):
    #     return FusedShell(shape_in=self.rudder_plns_fused.faces[4],
    #                       tool= [self.rudder_plns_fused.faces[5],
    #                              self.rudder_plns_fused.faces[6],
    #                              self.translate_rudder_closure_ribs_planes[0],
    #                              self.translate_rudder_closure_ribs_planes[1]
    #                              ]
    #                       )

    # @Part
    # def rudder_shell(self):
    #     return FusedShell(shape_in=self.rudder_shell_partly.faces[3],
    #                       tool= [self.rudder_shell_partly.faces[4],
    #                              self.rudder_shell_partly.faces[5],
    #                              self.rudder_shell_partly.faces[9],
    #                              self.rudder_shell_partly.faces[10]
    #                              ]
    #                       )
    @Part
    def back_up_fixed_shell(self):
        return FusedShell(shape_in=self.rudder_plns_fused.faces[7],
                          tool= [self.rudder_plns_fused.faces[8],
                                 self.rudder_plns_fused.faces[9],
                                 self.rudder_plns_fused.faces[10],
                                 self.rudder_plns_fused.faces[12]
                                 ]
                          )
    @Part
    def back_down_fixed_shell(self):
        return FusedShell(shape_in=self.rudder_plns_fused.faces[0],
                          tool= [self.rudder_plns_fused.faces[1],
                                 self.rudder_plns_fused.faces[2],
                                 self.rudder_plns_fused.faces[3],
                                 self.rudder_plns_fused.faces[11]
                                 ]
                          )



    @Part
    def fin_plns(self):
        return Plane(reference=Point(0, 0, self.p_zero + self.p_rib * child.index),
                     normal=Vector(0,
                                   0,
                                   1),
                     quantify=8
                     )
    @Part
    def fused_fin_ribs(self):
        return FusedShell(shape_in=self.front_shell,
                          tool = self.fin_plns)

    @Attribute(in_tree=True)
    def fixedpart_vtwing(self):
        return FusedShell(shape_in=self.fused_fin_ribs,
                          tool = [self.back_up_fixed_shell,self.back_down_fixed_shell])

    @Attribute(in_tree=False)
    def mac_def(self):
        sweep = radians(self.def_vwing.sweep_angle)
        taper = self.def_vwing.calculate_taper_ratio
        span = self.w_span
        cr = self.w_c_root

        z_loc=(2*span/6)*((1+2*taper)/(1+taper))
        x_loc=z_loc/tan((0.5*pi)-sweep)
        length=(2*cr/3)*((1+taper+taper**2)/(1+taper))
        return [x_loc, z_loc, length]

    @Attribute(in_tree=False)
    def ref_area(self):
        return 0.5* (self.w_c_root + self.def_vwing.w_c_tip) * self.w_span

    @Attribute
    def hingerib_pln_locs(self):
        if self.number_hinges == 2:
            Pointlist =  [Point(self.w_c_root - self.d_hinge,
                                self.rudder_shell.edges[3].position1.y - self.rhl_root,
                                self.translate_rudder_closure_ribs_planes[0].reference.z + self.dz_root_hinge_rib),
                          Point(self.w_c_root - self.d_hinge,
                                self.rudder_shell.edges[3].position2.y-self.rhl_tip,
                                self.translate_rudder_closure_ribs_planes[1].reference.z -self.dz_tip_hinge_rib)]
        return Pointlist

    @Part
    def hingerib_plns(self):
        return Plane(quantify= self.number_hinges,
                     reference=self.hingerib_pln_locs[child.index],
                     normal=Vector(0, 0, 1))

    @Part
    def fused_hingerib_plns(self):
        return FusedShell(shape_in = self.rudder_shell,
                          tool = self.hingerib_plns)

    @Part
    def hingerib_line(self):
        return LineSegment(self.hingerib_pln_locs[0],
                           self.hingerib_pln_locs[len(self.hingerib_pln_locs)-1],)

    @Part
    def actuatorrib_plns(self):
        return Plane()

    @Part
    def turn_rudder(self):
        return RotatedShape(shape_in=self.rudder_shell, rotation_point= self.hingerib_line.start,
                            vector=self.hingerib_line.direction_vector, angle=radians(30))















if __name__ == '__main__':
    from parapy.gui import display

    obj = VTailWing()
    display(obj)




