#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Fokker Aerostructures
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
# KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR
# PURPOSE.

from parapy.core import *
from parapy.geom import PolygonalFace, Vector, Point, Plane, IntersectedShapes

from buckling_loads import AnalyticPanelBucklingAnalysis
from section_analysis import SectionAnalysis

__all__ = [""]


class BayAnalysis(Base):
    #: Shear in x-direction.
    #: :type: list[float]
    Vx = Input()

    #: Shear in y-direction.
    #: :type: list[float]
    Vy = Input()

    #: Moment around x-axis
    #: :type: list[float]
    Mx = Input()

    #: Moment around y-axis
    #: :type: list[float]
    My = Input()

    #: Torsion moment
    #: :type: list[float]
    Mt = Input()

    #: x-coordinate of the position where the torsion and shear forces are defined.
    #: :type: list[float]
    ref_x = Input()

    #: y-coordinate of the position where the torsion and shear forces are defined.
    #: :type: list[float]
    ref_y = Input()

    #: Planes must be parallel.
    #: :type: list[parapy.geom.Plane]
    bay_planes = Input(in_tree=True)

    #: Number of tension points used as representation per face edge. Should be >= 3
    #: :type: integer
    N = Input(3, validator=val.GT(2))

    #: List of the right hand side skin faces
    #: Order: LE, main, TE
    #: :type: list[parapy.geom.Face]
    rhs_skin_faces = Input(in_tree=True)

    #: List of the left hand side skin faces,
    #: Order: LE, main, TE
    #: :type: list[parapy.geom.Face]
    lhs_skin_faces = Input(in_tree=True)

    #: List of the spar faces
    #: Order: FWD, AFT
    #: :type: list[parapy.geom.Face]
    spar_faces = Input(in_tree=True)

    #: List of the right hand side skin material thicknesses
    #: Order: LE, main, TE
    #: :type: list[float]
    rhs_skin_materials_t = Input()

    #: List of the left hand side skin material thicknesses
    #: Order: LE, main, TE
    #: :type: list[float]
    lhs_skin_materials_t = Input()

    #: List of the spar material thicknesses
    #: Order: FWD, AFT
    #: :type: list[float]
    spar_materials_t = Input()

    #: List of the right hand side skin material Young's moduli
    #: Order: LE, main, TE
    #: :type: list[float]
    rhs_skin_materials_E = Input()

    #: List of the left hand side skin material Young's moduli
    #: Order: LE, main, TE
    #: :type: list[float]
    lhs_skin_materials_E = Input()

    #: List of the spar material Young's moduli
    #: Order: FWD, AFT
    #: :type: list[float]
    spar_materials_E = Input()

    #: List of the right hand side skin material shear moduli
    #: Order: LE, main, TE
    #: :type: list[float]
    rhs_skin_materials_G = Input()

    #: List of the left hand side skin material shear moduli
    #: Order: LE, main, TE
    #: :type: list[float]
    lhs_skin_materials_G = Input()

    #: List of the spar material shear moduli
    #: Order: LE, main, TE
    #: :type: list[float]
    spar_materials_G = Input()

    #: List of the right hand side skin material D-matrices (D11, D22, D33, D12)
    #: Order: LE, main, TE
    #: :type: list[float]
    rhs_skin_materials_D = Input()

    #: List of the left hand side skin material D-matrices (D11, D22, D33, D12)
    #: Order: LE, main, TE
    #: :type: list[float]
    lhs_skin_materials_D = Input()

    #: List of the spar material D-matrices (D11, D22, D33, D12)
    #: Order: FWD, AFT
    #: :type: list[float]
    spar_materials_D = Input()

    @Attribute
    def faces(self):
        """List of all faces in the order expected by SectionAnalysis.

        :rtype: list[paray.geom.Surfaces
        """
        rhs_le, rhs_main, rhs_te = self.rhs_skin_faces
        lhs_le, lhs_main, lhs_te = self.lhs_skin_faces
        fwd, aft = self.spar_faces
        if not rhs_le.cog.x < rhs_main.cog.x < rhs_te.cog.x:
            msg = "The order of the provided RHS skin faces is incorrect, the order should be: " \
                  "leading edge skin, main skin, trailing edge skin."
            raise ValueError(msg)
        elif not lhs_le.cog.x < lhs_main.cog.x < lhs_te.cog.x:
            msg = "The order of the provided LHS skin faces is incorrect, the order should be: " \
                  "leading edge skin, main skin, trailing edge skin."
            raise ValueError(msg)
        elif not fwd.cog.x < aft.cog.x:
            msg = "The order of the provided spar faces is incorrect, the order should be: " \
                  "front spar, rear spar."
            raise ValueError(msg)
        return self.rhs_skin_faces + list(reversed(self.lhs_skin_faces)) + self.spar_faces

    @Attribute
    def edges(self):
        faces = self.faces

        edges = []
        for plane in self.bay_planes:
            lst = []
            for face in faces:
                lst.append(IntersectedShapes(shape_in=face,
                                             tool=plane).edges[0])
            edges.append(lst)
        return edges

    @Attribute
    def t_lsts(self):
        return self.rhs_skin_materials_t + list(
            reversed(self.lhs_skin_materials_t)) + self.spar_materials_t

    @Attribute
    def E_lsts(self):
        return self.rhs_skin_materials_E + list(
            reversed(self.lhs_skin_materials_E)) + self.spar_materials_E

    @Attribute
    def G_lsts(self):
        return self.rhs_skin_materials_G + list(
            reversed(self.lhs_skin_materials_G)) + self.spar_materials_G

    @Attribute
    def D_lsts(self):
        return self.rhs_skin_materials_D + list(
            reversed(self.lhs_skin_materials_D)) + self.spar_materials_D

    @Part
    def section_analysis(self):
        """Section Analysis at each plane from :attr: 'bay_planes'.

        :rtype: list[SectionAnalysis]
        """
        return SectionAnalysis(quantify=2,
                               Vx=self.Vx[child.index],
                               Vy=self.Vy[child.index],
                               Mx=self.Mx[child.index],
                               My=self.My[child.index],
                               Mt=self.Mt[child.index],
                               ref_x=self.ref_x[child.index],
                               ref_y=self.ref_y[child.index],
                               edges=self.edges[child.index],
                               t_lst=self.t_lsts,
                               E_lst=self.E_lsts,
                               G_lst=self.G_lsts,
                               N=self.N)

    @Attribute
    def panel_lengths(self):
        return [max(e1.start.distance(e2.start), e1.end.distance(e2.end)) for e1, e2 in
                zip(self.edges[0], self.edges[1])]

    @Attribute
    def panel_widths(self):
        return [max(e1.length, e2.length) for e1, e2 in zip(self.edges[0], self.edges[1])]

    @Part
    def buckling_analysis(self):
        """

        :rtype: parapy.core.Sequence[AnalyticPanelBucklingAnalysis]
        """
        return AnalyticPanelBucklingAnalysis(quantify=len(self.faces),
                                             panel_length=self.panel_lengths[child.index],
                                             panel_width=self.panel_widths[child.index],
                                             D_11=self.D_lsts[child.index][0],
                                             D_22=self.D_lsts[child.index][1],
                                             D_33=self.D_lsts[child.index][2],
                                             D_12=self.D_lsts[child.index][3],
                                             clamping_factor=0.0,
                                             compression_running_load=self.max_compression_lst[
                                                                          child.index] *
                                                                      self.t_lsts[child.index],
                                             shear_running_load=self.max_shear_lst[child.index])

    @Attribute
    def max_compression_lst(self):
        max_compression1 = self.section_analysis[0].max_compression_lst
        max_compression2 = self.section_analysis[1].max_compression_lst
        return [max(mc1, mc2) for mc1, mc2 in zip(max_compression1, max_compression2)]

    @Attribute
    def max_shear_lst(self):
        max_shears1 = self.section_analysis[0].max_shear_lst
        max_shears2 = self.section_analysis[1].max_shear_lst
        return [max(ms1, ms2) for ms1, ms2 in zip(max_shears1, max_shears2)]

    @Attribute
    def buckling_rf_combined(self):
        """Buckling reserve factors for combined compression and shear loads.

        :rtype: list[float]
        """
        return [analysis.rf_combined for analysis in self.buckling_analysis]

    @Attribute
    def rhs_skins_rfs(self):
        return self.buckling_rf_combined[:3]

    @Attribute
    def lhs_skins_rfs(self):
        return list(reversed(self.buckling_rf_combined[3:6]))

    @Attribute
    def spars_rfs(self):
        return self.buckling_rf_combined[6:]


if __name__ == '__main__':
    from parapy.gui import display

    rhs_le_skin = PolygonalFace([Point(100, 1000, 100), Point(-1000, 1000, 100),
                                 Point(-1000, 1000, -100), Point(100, 1000, -100)])
    rhs_main_skin = PolygonalFace([Point(2000, 1000, 100), Point(100, 1000, 100),
                                   Point(100, 1000, -100), Point(2000, 1000, -100)])
    rhs_te_skin = PolygonalFace([Point(3000, 0, 100), Point(2000, 1000, 100),
                                 Point(2000, 1000, -100), Point(3000, 0, -100)])
    lhs_te_skin = PolygonalFace([Point(3000, 0, 100), Point(2000, -1000, 100),
                                 Point(2000, -1000, -100), Point(3000, 0, -100)])
    lhs_main_skin = PolygonalFace([Point(2000, -1000, 100), Point(0, -1000, 100),
                                   Point(0, -1000, -100), Point(2000, -1000, -100)])
    lhs_le_skin = PolygonalFace([Point(0, -1000, 100), Point(-1000, -1000, 100),
                                 Point(-1000, -1000, -100), Point(0, -1000, -100)])
    fwd_spar = PolygonalFace([Point(100, 1000, 100), Point(0, -1000, 100),
                              Point(0, -1000, -100), Point(100, 1000, -100)])
    aft_spar = PolygonalFace([Point(2000, 1000, 100), Point(2000, -1000, 100),
                              Point(2000, -1000, -100), Point(2000, 1000, -100)])

    plane1 = Plane(Point(0, 0, 90), Vector(0, 0, 1), v_dim=500)
    plane2 = Plane(Point(0, 0, -90), Vector(0, 0, 1), v_dim=500)

    rhs_skin_faces = [rhs_le_skin, rhs_main_skin, rhs_te_skin]
    lhs_skin_faces = [lhs_le_skin, lhs_main_skin, lhs_te_skin]
    spar_faces = [fwd_spar, aft_spar]
    obj = BayAnalysis(Vx=[10000] * 2,
                      Vy=[10000] * 2,
                      Mx=[100000000] * 2,
                      My=[100000000] * 2,
                      Mt=[100000000] * 2,
                      ref_x=[0] * 2,
                      ref_y=[0] * 2,
                      bay_planes=[plane1, plane2],
                      rhs_skin_faces=rhs_skin_faces,
                      lhs_skin_faces=lhs_skin_faces,
                      spar_faces=spar_faces,
                      rhs_skin_materials_t=[1.0] * 3,
                      lhs_skin_materials_t=[1.0] * 3,
                      spar_materials_t=[1.0] * 2,
                      rhs_skin_materials_E=[72000] * 3,
                      lhs_skin_materials_E=[72000] * 3,
                      spar_materials_E=[72000] * 2,
                      rhs_skin_materials_G=[28000] * 3,
                      lhs_skin_materials_G=[28000] * 3,
                      spar_materials_G=[28000] * 2,
                      rhs_skin_materials_D=[[3069022, 3069022, 1051600.3, 965821.3]] * 3,
                      lhs_skin_materials_D=[[3069022, 3069022, 1051600.3, 965821.3]] * 3,
                      spar_materials_D=[[3069022, 3069022, 1051600.3, 965821.3]] * 2,
                      N=3)
    display(obj)
