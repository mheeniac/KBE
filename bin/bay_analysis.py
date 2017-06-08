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

from bay_analysis_tool.bay_analysis import BayAnalysis


def planes(obj):
    plane1 =TranslatedPlane(built_from=obj.def_v_tail_wing.rudder_plns.last,
                               displacement=Vector(0, 0, 0.02))
    plane2 =TranslatedPlane(built_from= obj.def_v_tail_wing.rudder_plns.first,
                               displacement=Vector(0, 0, -0.02))
    return plane1,plane2

def rhs_skin_faces(obj):
    return obj.def_v_tail_wing.fused_le_skin_right.faces[0], obj.def_v_tail_wing.main_skin_right.faces[0], obj.def_v_tail_wing.te_skin_right.faces[0]

def lhs_skin_faces(obj):
    return obj.def_v_tail_wing.fused_le_skin_left.faces[0], obj.def_v_tail_wing.main_skin_left.faces[0], obj.def_v_tail_wing.te_skin_left.faces[0]

def spar_faces(obj):
    return obj.def_v_tail_wing.rudder_front_spar.faces[0], obj.def_v_tail_wing.rudder_back_spar.faces[0]

def bay_planes(obj):
    return planes.plane1, planes.plane2

def bay_analysis(obj):
    analysis = BayAnalysis(Vx=[10000] * 2,
                  Vy=[10000] * 2,
                  Mx=[100000000] * 2,
                  My=[100000000] * 2,
                  Mt=[100000000] * 2,
                  ref_x=[0] * 2,
                  ref_y=[0] * 2,
                  bay_planes=bay_planes,
                  rhs_skin_faces=lhs_skin_faces,
                  lhs_skin_faces=rhs_skin_faces,
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
    return analysis

if __name__ == '__main__':
    from parapy.gui import display
    display([rhs_skin_faces, lhs_skin_faces, spar_faces, bay_planes, bay_analysis])
