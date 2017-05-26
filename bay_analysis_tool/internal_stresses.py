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
from parapy.geom import GeomBase, Point, LineSegment, PolygonalFace
from numpy import *

__all__ = [""]

OUTER = "outer"
INNER = "inner"


class TensionPoint(GeomBase):
    """Class with information on points that are part of the idealization of plates into points
    with tension properties and lines with shear properties.
    """

    #: ID of the Point, must be an integer.
    #: Used in shear_cell detection. Preferably start with the most forward point and go around
    #: clockwise on the outside of the #: shape.  Then define the internal structure.
    #: The assumption is that point with ID = 0 is where the skin is cut.
    #: :type: integer
    id = Input()
    #: Location of this tension point.
    #: :type: parapy.geom.Point
    location = Input(in_tree=True)
    #: The elements which the point is part of (necessary for finding loops).
    #: :type: list[ShearElement]
    connected_shear_els = Input()
    #: Young's (elastic) modulus in MPa.
    #: :type: float
    E = Input(derived)
    #: Area in mm2.
    #: :type: float
    A = Input(derived)

    @E.getter
    def E(self):
        """

        :rtype: float
        """
        els = self.connected_shear_els
        return sum([el.E for el in els]) / len(els)

    @A.getter
    def A(self):
        """

        :rtype: float
        """
        els = self.connected_shear_els
        return sum([0.5 * el.area for el in els])

    @Attribute
    def weighted_area(self):
        """

        :rtype: float
        """
        return self.E * self.A


class ShearElement(GeomBase):
    """Class with information on line elements that are part of the idealization of plates into
    points with tension properties and lines with shear properties.
    """

    #: Starting Point of the shear element.
    #: Preferably start with the most forward point and go around clockwise on the outside of the
    #: shape. Then define the internal structure. The assumption is that point 0 is where the skin
    #: is cut.
    #: :type: parapy.geom.Point
    start_pt = Input()

    #: Ending Point of the shear element.
    #: :type: parapy.geom.Point
    end_pt = Input()

    #: Type of element: "outer" or "internal".
    #: :type: string
    type = Input(validator=val.OneOf([OUTER, INNER]))

    #: Young's (elastic) modulus in MPa.
    #: :type: float
    E = Input()

    #: Shear modulus. Similar to E, but for shear in MPa.
    #: :type: float
    G = Input()

    #: Thickness of the shear element in mm.
    #: :type: float
    t = Input()

    @Attribute
    def area(self):
        """

        :rtype: float
        """
        return self.line_segment.length * self.t

    @Part
    def line_segment(self):
        """Shear element as a LineSegment."""
        return LineSegment(start=self.start_pt, end=self.end_pt)

    @Attribute
    def weighted_thickness(self):
        """

        :rtype: float
        """
        return self.G * self.t

    #: Placeholder for the shear stress in this beam from the cut open profile (step 1) in N/mm.
    #: :type: float
    _cut_shear_load = None

    #: Placeholder for the shear_cell stress in this beam (step 2) in N/mm.
    #: :type: float
    _shear_cell_shear_load = 0


class LoadCase(Base):

    #: Shear in x-direction in N.
    #: Positive in positive x-direction.
    #: :type: float
    Vx = Input()

    #: Shear in y-direction in N.
    #: Positive in positive y-direction.
    #: :type: float
    Vy = Input()

    #: Moment around x-axis in Nmm
    #: Positive rotation vector in positive x-direction.
    #: :type: float
    Mx = Input()

    #: Moment around y-axis in Nmm
    #: Positive rotation vector in positive y-direction.
    #: :type: float
    My = Input()

    #: Torsion moment in Nmm
    #: Positive rotation vector in positive z-direction.
    #: :type: float
    Mt = Input()

    #: x-coordinate in mm of the position where the torsion and shear forces are defined.
    #: :type: float
    ref_x = Input()

    #: y-coordinate in mm of the position where the torsion and shear forces are defined.
    #: :type: float
    ref_y = Input()


class MaterialTensionAndShear(Base):
    """Tension and shear stress distribution in a cross-section using panel sections
    idealized into tension load bearing points and shear load bearing shear elements."""

    #: Point distribution over the cross-section.
    #: :type: list[TensionPoint]
    tension_pts = Input()

    #: Shear elements connecting the :attr: 'tension_pts'.
    #: :type: list[ShearElement]
    shear_els = Input()

    #: Load case for the cross-section.
    #: :type: LoadCase
    load_case = Input()

    @Attribute
    def center_of_stiffness(self):
        """Center of stiffness in mm.
        Notice: Based on weighted areas using the Young's modulus (E) as weighting factor.

        :rtype: parapy.geom.Point
        """
        Sx = 0.0
        Sy = 0.0
        EA_sum = 0.0
        for pt in self.tension_pts:
            EA = pt.weighted_area
            # Product of Inertia
            Sx += EA * pt.location.x
            Sy += EA * pt.location.y
            EA_sum += EA

        return Point(x=Sx / EA_sum, y=Sy / EA_sum, z=0.0)

    @Attribute
    def torsion_moment_at_cs(self):
        """Translated torsion moment (ie Mt) to the :attr: 'center_of_stiffness' in Nmm.

        :rtype: float
        """
        lc = self.load_case
        cs_x = self.center_of_stiffness.x
        cs_y = self.center_of_stiffness.y
        return lc.Mt + lc.Vy * (cs_x - lc.ref_x) + lc.Vx * (cs_y - lc.ref_y)

    @Attribute
    def av_tension_modulus(self):
        """Average Young's Modulus in MPa.

        :rtype: float
        """
        total_EA = 0
        total_A = 0
        for pt in self.tension_pts:
            EA = pt.weighted_area
            A = pt.A
            total_EA += EA
            total_A += A
        return total_EA / total_A

    @Attribute
    def av_shear_modulus(self):
        """Average Shear Modulus G in MPa.

        :rtype: float
        """
        total_Gl_t = 0
        total_l_t = 0
        for shear_el in self.shear_els:
            l_div_t = shear_el.line_segment.length / shear_el.t
            total_Gl_t += shear_el.G * l_div_t
            total_l_t += l_div_t
        return total_Gl_t / total_l_t

    @Attribute
    def weighted_moment_of_inertia_xx_yy(self):
        """Moments of Inertia around y-axis and x-axis around the :attr: 'center_of_stiffness' in mm4.
        Notice: Based on weighted areas using the Young's modulus (E) as weighting factor.

        :rtype: tuple[float]
        """
        center_of_stiffness = self.center_of_stiffness
        E_average = self.av_tension_modulus
        EIyy = 0
        EIxx = 0
        for pt in self.tension_pts:
            pt_x = pt.location.x
            pt_y = pt.location.y
            EA = pt.weighted_area
            EIyy += EA * (center_of_stiffness.x - pt_x)**2
            EIxx += EA * (center_of_stiffness.y - pt_y)**2
        return EIyy / E_average, EIxx / E_average

    @Attribute
    def normal_stresses(self):
        """Stresses in the idealized tension points in z-direction in MPa.
        The stresses are returned in the same order as the tension points list specified in the input.

        :rtype: list[float]
        """
        lc = self.load_case
        Mx = lc.Mx
        My = lc.My
        Iyy, Ixx = self.weighted_moment_of_inertia_xx_yy
        center_of_stiffness = self.center_of_stiffness

        stress_lst = []
        for pt in self.tension_pts:
            pt_x = pt.location.x
            pt_y = pt.location.y
            stress_lst.append((My/Iyy) * (center_of_stiffness.x - pt_x) -
                              (Mx/Ixx) * (center_of_stiffness.y - pt_y))

        return stress_lst

    @Attribute
    def outer_pts(self):
        """The idealized tension points on the outside of the cross section.

        :rtype: list[TensionPoint]
        """
        outer_pts = []
        for pt in self.tension_pts:
            shear_els = pt.connected_shear_els
            for shear_el in shear_els:
                # If the point lies on minimal 1 skin element, we need it
                if shear_el.type == OUTER:
                    outer_pts.append(pt)
                    break               # when we find one match we don't need to look any further
        return outer_pts

    # Helper method to find the shear stresses in the elements/beams
    def walk_for_shear(self, pt, pts, cur_path, max_id, last_elem):
        """Depth-First-Search based algorithm to find the shear stresses in every element.
        Loosely based on: 
            https://algocoding.wordpress.com/2015/04/02/detecting-shear_cell_belonging_to_each_pt-in-a-directed-graph-with-dfs-python/
        :param IdealizedTensionPoint pt: TensionPoint of interest
        :param list[IdealizedTensionPoint] pts: List of all possible IdealizedTensionPoints to choose from
        :param list[TensionPoint] cur_path:
        :param integer max_id:
        :param ShearElement last_elem:
        :rtype: list[IdealizedTensionPoint]
        """
        lc = self.load_case
        Vx = lc.Vx
        Vy = lc.Vy
        Iyy, Ixx = self.weighted_moment_of_inertia_xx_yy
        cs = self.center_of_stiffness
        E_av = self.av_tension_modulus

        last_pt = cur_path[-1] if len(cur_path) > 0 else pt
        cur_path.append(pt)

        next_pt = None
        for shear_el in pt.connected_shear_els:
            # Check for Points on the same elements > neighbours
            if shear_el.type == OUTER:
                for pt_i in pts:
                    if pt != pt_i and not(pt.id == 0 and pt_i.id == max_id) and pt_i != last_pt:
                        for shear_el_i1 in pt_i.connected_shear_els:
                            # Lie on same element > neighbours
                            if shear_el_i1 == shear_el:
                                xi = pt_i.location.x
                                yi = pt_i.location.y
                                A = pt_i.weighted_area / E_av

                                # We need the next element
                                for shear_el_n in pt_i.connected_shear_els:
                                    if shear_el_n != shear_el_i1 and shear_el_n.type == OUTER:
                                        shear_el_n._cut_shear_load = last_elem._cut_shear_load +\
                                                                  ((Vx * A * (xi - cs.x)) / Iyy) +\
                                                                  ((Vy * A * (yi - cs.y)) / Ixx)
                                        next_pt = pt_i
                                        last_elem = shear_el_n

        # This part makes it recursive.
        if next_pt is not None:
            # trigger a next loop as long as next_pt is not None
            if next_pt in cur_path:
                cur_path.append(next_pt)
                return cur_path
            # Keep looking
            else:
                return self.walk_for_shear(next_pt, pts, cur_path, max_id, last_elem)
        # No loop is triggered if we reach the end point and next_pt is None
        else:
            return []

    @Attribute
    def cut_shear_el_loads(self):
        """Return list of shear loads, assuming all shear cells are cut.

        :rtype: list[float]
        """
        all_pts = self.tension_pts
        skin_pts = self.outer_pts
        max_id = max([p.id for p in skin_pts])
        current_path = []

        # Initialize (calculate the first element)
        lc = self.load_case
        Vx = lc.Vx
        Vy = lc.Vy
        Iyy, Ixx = self.weighted_moment_of_inertia_xx_yy
        cs = self.center_of_stiffness

        pt = skin_pts[0]  # assumption that point 0 is where the skin is cut.....
        pt_x = pt.location.x
        pt_y = pt.location.y
        A = pt.weighted_area / self.av_tension_modulus
        last_elem = pt.connected_shear_els[0]
        last_elem._cut_shear_load = ((Vx * A * (pt_x - cs.x)) / Iyy) + \
                                    ((Vy * A * (pt_y - cs.y)) / Ixx)
        current_path.append(pt)

        if self.walk_for_shear(pt, skin_pts, current_path, max_id, last_elem) is not None:
            cut_shear_loads = [shear_el._cut_shear_load for shear_el in self.shear_els
                               if shear_el._cut_shear_load is not None]
            return cut_shear_loads

    @Attribute
    def areas_between_shear_els_and_cs(self):
        """List of triangular areas that are defined by the start point and end point
        of the :attr: 'shear_els' and by the :attr: 'center_of_stiffness'.

        :rtype: list[float]
        """
        # Initialize starting values
        shear_els = self.shear_els
        cs = self.center_of_stiffness

        area_lst = []
        for shear_el in shear_els:
            if shear_el.type == OUTER:
                pt_start = shear_el.start_pt
                pt_end = shear_el.end_pt
                pt_start_x = pt_start.x - cs.x
                pt_start_y = pt_start.y - cs.y

                pt_end_x = pt_end.x - cs.x
                pt_end_y = pt_end.y - cs.y
                area_lst.append(0.5 * abs(pt_start_x * pt_end_y - pt_start_y * pt_end_x))

        return area_lst

    @Attribute
    def sum_moment_cut_structure(self):
        """Return the contribution of the :attr: 'cut_shear_el_loads' to the torsional moment.
        Calculated as: SUM(2 * :attr: 'areas_between_shear_els_and_cs'_i * :attr: 'cut_shear_el_loads'_i)

        :rtype: float
        """
        area = self.areas_between_shear_els_and_cs
        q_cut = self.cut_shear_el_loads

        return 2 * sum([area[i_shear_el] * q_cut[i_shear_el] for i_shear_el in range(len(area))])

    # Helper method to find shear_cell_belonging_to_each_pt
    def look_for_shear_cell(self, pe_set, pts, cur_path, max_id):
        """Depth-First-Search based algorithm to find the :attr: 'shear_cell_belonging_to_each_pt'.
        (i.e. all closed contours) in a graph.

        Loosely based on:
            https://algocoding.wordpress.com/2015/04/02/detecting-shear_cell_belonging_to_each_pt-in-a-directed-graph-with-dfs-python/

        ---- determine the circles in the structure cross-section ----
        I can use DFS:
            https://algocoding.wordpress.com/2015/04/02/detecting-shear_cell_belonging_to_each_pt-in-a-directed-graph-with-dfs-python/
            http://stackoverflow.com/questions/15723256/algorithm-to-get-shear_cell-in-graph
        I do need to chane it a bit, since I want to detect what points belong to which shear_cell.
        Also, I only need the loops that run via the nearest spars (and not any "outer" loops)

        Circle detection algorithm:
        Start on a outer point
        0. check if current_point is already logged in the current circle. yes: we got a
        circle! no: go to 1.

        1. Log the point as part of a possible circle
        2. Check it's neighbouring Points that are not already logged
               If no neighbours > no circle
        3. Check if one of the neighbouring Points is on a internal. yes: go to 4./ no: go to 1.

        4. Log the internal point as part of the possible circle. AND if preset, log the other
        neighbour point (outer) as a starting point of a possible circle.
        5. Check it's neighbouring Points that are not already logged
              EXTRA CHECK: After the first internal point there MUST be another internal point!
                          If no neighbours > no circle
        6. Check if one of the neighbouring Points is on a outer. yes: go to 7./ no: go to 4.

        7. Log the internal point as part of the possible circle.
        8. Check it's neighbouring Points that are not already logged
              If no neighbours > no circle
        9. Choose the next outer point based on which index is higher (assumption: the points are
        defined in a circular fashion!)
        10. go to 0.

        If starting points available, perform algorithm on them
        :param tuple[TensionPoint, ShearElement] pe_set:
        :param list[TensionPoint] pts: List of all possible IdealizedTensionPoints to choose from
        :param list[tuple[TensionPoint, ShearElement]] cur_path:
        :param integer max_id:
        :rtype: list[tuple[TensionPoint, ShearElement]]
        """
        last_pe_set = cur_path[-1] if len(cur_path) > 0 else pe_set
        cur_path.append(pe_set)
        pt_i = pe_set[0]

        internal_pts = []
        outer_pts = []
        for shear_el_i in pt_i.connected_shear_els:
            # Check for nodes on the same elements > neighbours
            for pt_n in pts:
                if pt_i != pt_n and not(pt_i.id == 0 and pt_n.id == max_id) and pt_n != last_pe_set[0]:
                    for shear_el_n in pt_n.connected_shear_els:
                        # Lie on same element > neighbours
                        if shear_el_n == shear_el_i:
                            if shear_el_n.type == INNER:
                                internal_pts.append(tuple([pt_n, shear_el_n]))
                            # Via a internal element we can go to a lower index skin_pt,
                            # but not through an outer element!
                            elif pt_n.id > pt_i.id or (pt_i.id == max_id and pt_n.id == 0):
                                outer_pts.append(tuple([pt_n, shear_el_n]))

        # If there is a internal-pe_set > take it. Otherwise take the outer-pe_set with the highest index
        # This is based on the assumption that the outer-points are defined in circular fashion
        next_pe_set = internal_pts[0] if len(internal_pts) > 0 and not (internal_pts[0] in cur_path) \
            else (outer_pts[-1] if len(outer_pts) > 0 else None)

        if next_pe_set is not None:
            # loop!
            if next_pe_set[0] in [pe_set[0] for pe_set in cur_path]:
                cur_path.append(next_pe_set)
                return cur_path
            # Keep looking
            else:
                return self.look_for_shear_cell(next_pe_set, pts, cur_path, max_id)
        # We end_pt with None > no loop
        else:
            return []

    @Attribute
    def shear_cell_belonging_to_each_pt(self):
        """Return tuple of two list of lists. The first contains a list of lists of pts where
        each list of pts form a shear_cell. 
        
        The second is a list of list of elements where each list of elements forms a shear_cell. 
        The elements correspond to the pts in the same first tuple
        element.

        :rtype: list[list[TensionPoint]]
        """
        skin_points = self.outer_pts
        all_pts = self.tension_pts
        max_id = max([p.id for p in skin_points])

        shear_cells = []
        cur_path = []

        for pt in skin_points:
            cur_path = self.look_for_shear_cell(tuple([pt, None]), all_pts, cur_path, max_id)
            shear_cells.append(cur_path)
            cur_path = []

        return [shear_cell for shear_cell in shear_cells if len(shear_cell) > 0]

    @Attribute
    def unique_shear_cells(self):
        """Return unique values.
        First order the shear_cell_belonging_to_each_pt based on point.id. 
        Turn it into a set so only the unique shear_cell_belonging_to_each_pt are left. 
        Then turn back into a list.

        :rtype: list[list[list[TensionPoint, ShearElement]]]
        """
        # NB: first step contains only starting point and no shear element, \
        # so we do not consider it.
        unique_shear_cells_as_tuples = set(tuple(sorted(shear_cell[1:], key=lambda l: l[0].id))
                                           for shear_cell in self.shear_cell_belonging_to_each_pt)
        unique_shear_cells_as_lst_of_lst = [list(cell) for cell in unique_shear_cells_as_tuples]
        return sorted(unique_shear_cells_as_lst_of_lst, key=lambda l: l[0][0].id)

    @Attribute
    def shear_cell_areas(self):
        """Areas within the shear_cell_belonging_to_each_pt.

        :rtype: list[float]
        """
        area_lst = []
        for shear_cell in self.unique_shear_cells:
            poly_face = PolygonalFace(points=[step[0].location for step in shear_cell])
            area_lst.append(poly_face.area)

        return area_lst

    @Attribute
    def summed_thetas(self):
        """Contribution of the clean shear element stresses to the twist of the shear_cell.

        :rtype: collection.sequence[float]
        """
        # Purely a call to make sure it has been calculated (since we use it here)
        if self.cut_shear_el_loads is not None:
            theta_lst = []
            sum_theta = 0
            for shear_cell in self.unique_shear_cells:
                # per step in shear_cell
                for step in shear_cell:
                    shear_el = step[1]
                    weighted_t = shear_el.weighted_thickness / self.av_shear_modulus
                    if shear_el._cut_shear_load is not None:
                        sum_theta += shear_el._cut_shear_load * \
                                     shear_el.line_segment.length / weighted_t

                theta_lst.append(sum_theta)
                sum_theta = 0

            return theta_lst

    @Attribute
    def summed_ds(self):
        """Factors to multiply the shear_cell shear with.

        :rtype: collection.sequence[float]
        """
        # Purely a call to make sure it has been calculated (since we use it here)
        if self.cut_shear_el_loads is not None:
            ds_lst = []
            sum_ds = 0
            for shear_cell in self.unique_shear_cells:
                # per step in shear_cell
                for step in shear_cell:
                    shear_el = step[1]
                    weighted_t = shear_el.weighted_thickness / self.av_shear_modulus
                    sum_ds += shear_el.line_segment.length / weighted_t

                ds_lst.append(sum_ds)
                sum_ds = 0

            return ds_lst

    @Attribute
    def internal_el_shear_cell_contributions(self):
        """internal contributions to the shear_cell shear theta formulas per shear_cell.

        :rtype: collection.sequence[collection.sequence[float]]
        """
        internal_contours = []
        contrib_lst = []
        shear_cells = self.unique_shear_cells
        for shear_cell_i in shear_cells:
            for shear_cell_n in shear_cells:
                # check with other shear_cell_belonging_to_each_pt
                if shear_cell_i != shear_cell_n:
                    for step_i in shear_cell_i:
                        for step_n in shear_cell_n:
                            if step_i[1] == step_n[1]:
                                weighted_t = step_i[1].weighted_thickness / self.av_shear_modulus
                                contrib_lst.append(step_i[1].line_segment.length / weighted_t)
            internal_contours.append(contrib_lst)
            contrib_lst = []

        return internal_contours

    @Attribute
    def shear_cell_shears(self):
        """Shear loads going around in each closed shear cell.

        :rtype: list[float]
        """
        areas = self.shear_cell_areas

        if len(areas) == 1:
            Mt = self.torsion_moment_at_cs
            A_shear_cell = self.shear_cell_areas[0]
            return [(Mt - self.sum_moment_cut_structure) / (2 * A_shear_cell)]
        elif len(areas) == 2:
            return self.two_shear_shear_cells()
        elif len(areas) == 3:
            return self.three_shear_shear_cells()
        else:
            raise Exception('Only cross sections with one, two or three shearcells are possible.' +
                            'Please make sure that one, two or three shearcells exist.')

    def two_shear_shear_cells(self):
        """Shear loads if two shear cells exist.

        :rtype: list[float]
        """
        Mt = self.torsion_moment_at_cs
        A_shear_cell = self.shear_cell_areas
        sum_thetas = self.summed_thetas
        sum_ds = self.summed_ds

        if len(A_shear_cell) == 2:
            f10 = A_shear_cell[1] / A_shear_cell[0]

            bb1 = Mt - self.sum_moment_cut_structure
            bb2 = f10 * sum_thetas[0] - sum_thetas[1]
            bb = matrix([[bb1],
                         [bb2]])

            AA1 = [2 * A_shear_cell[0], 2 * A_shear_cell[1]]

            spar_contrs = self.internal_el_shear_cell_contributions
            spar1_contr = spar_contrs[0][0]
            AA2 = [-f10 * sum_ds[0] - spar1_contr, sum_ds[1] + f10 * spar1_contr]
            AA = matrix([AA1,
                         AA2])

            A_inv = linalg.inv(AA)
            shear_load = dot(A_inv, bb)
            return [shear_load.item(0), shear_load.item(1)]

    def three_shear_shear_cells(self):
        """Shear loads if three shear cells exist.

        :rtype: list[float]
        """
        Mt = self.torsion_moment_at_cs
        A_shear_cell = self.shear_cell_areas
        sum_thetas = self.summed_thetas
        sum_ds = self.summed_ds

        if len(A_shear_cell) == 3:
            f10 = A_shear_cell[1] / A_shear_cell[0]
            f21 = A_shear_cell[2] / A_shear_cell[1]

            bb1 = Mt - self.sum_moment_cut_structure
            bb2 = f10 * sum_thetas[0] - sum_thetas[1]
            bb3 = f21 * sum_thetas[1] - sum_thetas[2]
            bb = matrix([[bb1],
                         [bb2],
                         [bb3]])

            AA1 = [2 * A_shear_cell[0], 2 * A_shear_cell[1], 2 * A_shear_cell[2]]

            spar_contrs = self.internal_el_shear_cell_contributions
            spar1_contr = spar_contrs[0][0]
            spar2_contr = spar_contrs[2][0]
            AA2 = [-f10 * sum_ds[0] - spar1_contr, sum_ds[1] + f10 * spar1_contr, -spar2_contr]
            AA3 = [f21 * spar1_contr, -f21 * sum_ds[1] - spar2_contr, sum_ds[2] + f21 * spar2_contr]
            AA = matrix([AA1,
                         AA2,
                         AA3])

            A_inv = linalg.inv(AA)
            q = dot(A_inv, bb)
            return [q.item(0), q.item(1), q.item(2)]

    @Attribute
    def shear_stresses(self):
        """Summation of shear load in cut structure and closed shear cell shears in N/mm.
        The shear is given in the order of the shear elements specified in the input.

        :rtype: list[float]
        """

        # Make sure that the cut shear element stresses have been run
        unused1 = self.cut_shear_el_loads
        # Also make sure that the shear cell shears have been run
        unused2 = self.shear_cell_shears

        # Extra check to make sure it is set to 0 (ensuring no dependency _cut_shear_load)
        for shear_cell in self.unique_shear_cells:
            for shear_el in shear_cell:
                shear_el[1]._shear_cell_shear_load = 0

        for i_cell, shear_cell in enumerate(self.unique_shear_cells):
            q_closed = self.shear_cell_shears[i_cell]
            for shear_el in shear_cell:
                if shear_el[1]._shear_cell_shear_load == 0:
                    shear_el[1]._shear_cell_shear_load = q_closed
                else:
                    shear_el[1]._shear_cell_shear_load -= q_closed

        q = [((shear_el._cut_shear_load if shear_el._cut_shear_load is not None else 0) +
              shear_el._shear_cell_shear_load) for shear_el in self.shear_els]

        return q




