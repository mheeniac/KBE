#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Fokker Aerostructures
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
# KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR
# PURPOSE.

from operator import attrgetter

from parapy.core import *
from parapy.geom import Plane, Point, IntersectedShapes, Vector, PolygonalFace
from internal_stresses import TensionPoint, ShearElement, LoadCase, MaterialTensionAndShear
from parapy.geom import BezierCurve
__all__ = [""]


class SectionAnalysis(Base):

    #: Shear in x-direction.
    #: :type: float
    Vx = Input()

    #: Shear in y-direction.
    #: :type: float
    Vy = Input()

    #: Moment around x-axis
    #: :type: float
    Mx = Input()

    #: Moment around y-axis
    #: :type: float
    My = Input()

    #: Torsion moment
    #: :type: float
    Mt = Input()

    #: x-coordinate of the position where the torsion and shear forces are defined.
    #: :type: float
    ref_x = Input()

    #: y-coordinate of the position where the torsion and shear forces are defined.
    #: :type: float
    ref_y = Input()

    #: edges of the rudder components
    #: order: rhs_le, rhs_main, rhs_te, lhs_te, lhs_main, lhs_le, fwd_spar, aft_spar
    #: :type: list[parapy.geom.Face]
    edges = Input(in_tree=True)

    #: thicknesses of the rudder components
    #: order: rhs_le, rhs_main, rhs_te, lhs_te, lhs_main, lhs_le, fwd_spar, aft_spar
    #: :type: list[float}
    t_lst = Input()

    #: Young's moduli of the rudder components
    #: order: rhs_le, rhs_main, rhs_te, lhs_te, lhs_main, lhs_le, fwd_spar, aft_spar
    #: :type: list[float}
    E_lst = Input()

    #: Shear moduli of the rudder components
    #: order: rhs_le, rhs_main, rhs_te, lhs_te, lhs_main, lhs_le, fwd_spar, aft_spar
    #: :type: list[float}
    G_lst = Input()

    #: Number of tension points used as representation per face edge. Should be >= 3
    #: :type: int
    N = Input(validator=val.GT(2))

    @Attribute
    def types_lst(self):
        """All types used for the shear elements.

        :rtype: list[str]
        """
        all_types = ["outer"] * 6 + ["inner"] * 2
        return all_types

    @Attribute
    def points_per_edge(self):
        """All unique points, used as locations for the tension points.

        :rtype: list[list[parapy.geom.Point]]
        """
        edges = self.edges
        n = self.N
        fn = lambda edge, idx: sorted(edge.equispaced_points(n), key=lambda l: l[idx])

        arr = [fn(edges[0], 0)]

        for edge in edges[1:3]:
            pts = fn(edge, 0)
            # take last point from previous edge
            pts[0] = arr[-1][-1]
            arr.append(pts)

        for edge in edges[3:6]:
            pts = fn(edge, 0)
            pts.reverse()
            # take last point from previous edge
            pts[0] = arr[-1][-1]
            arr.append(pts)

        pts_fwd_spar = fn(edges[6], 1)
        pts_fwd_spar[0] = arr[-1][0]
        pts_fwd_spar[-1] = arr[0][-1]

        pts_aft_spar = fn(edges[7], 1)
        pts_aft_spar[0] = arr[-2][0]
        pts_aft_spar[-1] = arr[1][-1]
        arr.append(pts_fwd_spar)
        arr.append(pts_aft_spar)

        return arr

    @Attribute
    def shear_elements_per_edge(self):
        """All shear elements required for the internal stress analysis.

        :rtype: list[list[ShearElement]]
        """
        arr = []
        for pts, E, G, t, type_ in \
                zip(self.points_per_edge, self.E_lst, self.G_lst, self.t_lst, self.types_lst):
            lst = []
            for pt1, pt2 in pairwise(pts):
                elm = ShearElement(start_pt=pt1, end_pt=pt2, type=type_, E=E, G=G, t=t)
                lst.append(elm)
            arr.append(lst)
        return arr

    @Attribute
    def tension_points(self):
        """All tension points required for the internal stress analysis.

        :rtype: list[TensionPoint]
        """
        arr_pts = self.points_per_edge
        arr_elms = self.shear_elements_per_edge
        arr = []

        # first, populate entire array (for each edge)
        i = [0]
        visited = {}

        def make_tension_point(pt, elms=()):
            if pt in visited:
                id_ = visited[pt]
            else:
                id_ = i[0]
                visited[pt] = id_
                i[0] += 1
            return TensionPoint(id=id_, location=pt, connected_shear_els=elms)

        for pts, elms in zip(arr_pts, arr_elms):
            lst = [make_tension_point(pts[0])]
            for pt, (elm1, elm2) in zip(pts[1:-1], pairwise(elms)):
                tpt = make_tension_point(pt, (elm1, elm2))
                lst.append(tpt)
            lst.append(make_tension_point(pts[-1]))
            arr.append(lst)

        # fix the start and end points of outer skins
        arr[0][0].connected_shear_els = [arr[0][1].connected_shear_els[0]]
        arr[5][-1].connected_shear_els = [arr[5][-2].connected_shear_els[-1]]

        # fix the TE point
        arr[2][-1].connected_shear_els = [arr[2][-2].connected_shear_els[-1],
                                          arr[3][1].connected_shear_els[0]]
        arr[3][0] = arr[2][-1]  # remove duplicate

        # fix T-junction fwd-spar rhs
        arr[0][-1].connected_shear_els = [arr[0][-2].connected_shear_els[-1],
                                          arr[1][1].connected_shear_els[0],
                                          arr[6][-2].connected_shear_els[-1]]
        arr[1][0] = arr[6][-1] = arr[0][-1]
        # fix T-junction aft-spar rhs
        arr[1][-1].connected_shear_els = [arr[1][-2].connected_shear_els[-1],
                                          arr[2][1].connected_shear_els[0],
                                          arr[7][-2].connected_shear_els[-1]]
        arr[2][0] = arr[7][-1] = arr[1][-1]  # remove duplicate
        # fix T-junction aft-spar lhs
        arr[3][-1].connected_shear_els = [arr[3][-2].connected_shear_els[-1],
                                          arr[4][1].connected_shear_els[0],
                                          arr[7][1].connected_shear_els[0]]
        arr[4][0] = arr[7][0] = arr[3][-1]  # remove duplicate
        # fix T-junction fwd-spar lhs
        arr[4][-1].connected_shear_els = [arr[4][-2].connected_shear_els[-1],
                                          arr[5][1].connected_shear_els[0],
                                          arr[6][1].connected_shear_els[0]]
        arr[5][0] = arr[6][0] = arr[4][-1]  # remove duplicate

        lst = set([pt for lst in arr for pt in lst])
        return sorted(lst, key=attrgetter("id"))

    @Attribute
    def shear_elements(self):
        """Flat list containing all shear elements required for the internal stress analysis.

        :rtype: list[ShearElement]
        """
        return [el for lst in self.shear_elements_per_edge for el in lst]

    @Part
    def load_case(self):
        """The load case used for the internal stress analysis.

        :rtype: LoadCase
        """
        return LoadCase(Vx=self.Vx,
                        Vy=self.Vy,
                        Mx=self.Mx,
                        My=self.My,
                        Mt=self.Mt,
                        ref_x=self.ref_x,
                        ref_y=self.ref_y)

    @Part
    def internal_stresses(self):
        """

        :rtype: MaterialTensionAndShear
        """
        return MaterialTensionAndShear(tension_pts=self.tension_points,
                                       shear_els=self.shear_elements,
                                       load_case=self.load_case)

    @Attribute
    def max_compression_lst(self):
        """

        :rtype: list[float]
        """
        lst = []
        n = self.N - 1
        stresses = self.internal_stresses.normal_stresses
        lst.append(min(stresses[n*0:n*1+1]))  # rhs_le
        lst.append(min(stresses[n*1:n*2+1]))  # rhs_ma
        lst.append(min(stresses[n*2:n*3+1]))  # rhs_te
        lst.append(min(stresses[n*3:n*4+1]))  # lhs_te
        lst.append(min(stresses[n*4:n*5+1]))  # lhs_ma
        lst.append(min(stresses[n*5:n*6+1]))  # lhs_le
        lst.append(min([stresses[n*5]] + stresses[n*6+1:n*7] + [stresses[n*1]]))  # fwd_spar
        lst.append(min([stresses[n*4]] + stresses[n*7:n*8] + [stresses[n*2]]))    # aft_spar
        return lst

    @Attribute
    def max_shear_lst(self):
        """

        :rtype: list[float]
        """
        max_shear_lst = []
        N = self.N
        shear_stresses = self.internal_stresses.shear_stresses
        for i in xrange(len(self.edges)):
            sub_list = shear_stresses[(N-1)*i:(N-1)*(i+1)]
            max_shear_lst.append(max([abs(entry) for entry in sub_list]))
        return max_shear_lst


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

    faces = [rhs_le_skin, rhs_main_skin, rhs_te_skin,
              lhs_te_skin, lhs_main_skin, lhs_le_skin,
              fwd_spar, aft_spar]
    plane = Plane(Point(0, 0, 90), Vector(0, 0, 1))
    edges = []
    for face in faces:
        edges.append(IntersectedShapes(shape_in=face,
                                       tool=plane).edges[0])
    obj = SectionAnalysis(Vx=1000,
                          Vy=1000,
                          Mx=1000,
                          My=1000,
                          Mt=1000,
                          ref_x=0,
                          ref_y=0,
                          edges=edges,
                          t_lst=[0.1] * 8,
                          E_lst=[72000] * 8,
                          G_lst=[30000] * 8,
                          N=3)
    display(obj)
