#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Fokker Aerostructures
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
# KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR
# PURPOSE.

from parapy.geom import *

from bay_analysis import BayAnalysis

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
bay_planes = [plane1, plane2]
obj = BayAnalysis(Vx=[10000] * 2,
                  Vy=[10000] * 2,
                  Mx=[100000000] * 2,
                  My=[100000000] * 2,
                  Mt=[100000000] * 2,
                  ref_x=[100,200],
                  ref_y=[200,400],
                  bay_planes=bay_planes,
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

if __name__ == '__main__':
    from parapy.gui import display

    display([rhs_skin_faces, lhs_skin_faces, spar_faces, bay_planes, obj])
