import parapy.lib.avl as avl
from parapy.geom import Point
from math import *


def section_main_root(obj):
    return avl.AirfoilCurveSection(curve_in=obj.translate_main_wing[0].edges[0])


def section_main_tip(obj):
    return avl.AirfoilCurveSection(curve_in=obj.translate_main_wing[0].edges[2])


def main_surface(obj):
    return avl.Surface(name="Main Wing",
                       sections=[section_main_root(obj), section_main_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0,
                       y_duplicate=0.0)


def section_htp_root(obj):
    return avl.AirfoilCurveSection(curve_in=obj.translate_h_tail_wing[0].edges[0])


def section_htp_tip(obj):
    return avl.AirfoilCurveSection(curve_in=obj.translate_h_tail_wing[0].edges[2])


def htp_surface(obj):
    return avl.Surface(name="HTP",
                       sections=[section_htp_root(obj), section_htp_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0,
                       y_duplicate=0.0)


def rudder_root_le_te_points(obj):
    # Trailing Edge
    pt_te_x = obj.def_v_tail_wing.closure_ribs[0].vertices[0].point.x
    pt_te_x = pt_te_x + v_tail_xshift(obj)
    # pt_te_y = obj.def_v_tail_wing.closure_ribs[0].vertices[0].point.y
    pt_te_y = 0
    pt_te_z = obj.def_v_tail_wing.closure_ribs[0].vertices[0].point.z + obj.cabin_diameter

    # Leading Edge
    # pt_le_y = obj.def_v_tail_wing.closure_ribs[0].vertices[1].point.y - 0.5* \
    #           (obj.def_v_tail_wing.closure_ribs[0].vertices[1].point.y-obj.def_v_tail_wing.closure_ribs[0].vertices[2].point.y)
    pt_le_y = 0
    pt_le_x = obj.def_v_tail_wing.closure_ribs[0].vertices[1].point.x
    pt_le_x = pt_le_x + v_tail_xshift(obj)
    pt_le_z = obj.def_v_tail_wing.closure_ribs[0].vertices[1].point.z + obj.cabin_diameter

    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)
    pt_te = Point(pt_te_x, pt_te_y, pt_te_z)
    return pt_le, pt_te


def rudder_tip_le_te_points(obj):
    # Trailing Edge
    pt_te_x = obj.def_v_tail_wing.closure_ribs[1].vertices[0].point.x
    pt_te_y = 0
    pt_te_x = pt_te_x + v_tail_xshift(obj)
    pt_te_z = obj.def_v_tail_wing.closure_ribs[1].vertices[0].point.z + obj.cabin_diameter

    # Leading Edge
    # pt_le_y = obj.def_v_tail_wing.closure_ribs[1].vertices[1].point.y - 0.5 * \
    #                                                                  (obj.def_v_tail_wing.closure_ribs[1].vertices[
    #                                                                       1].point.y -
    #                                                                   obj.def_v_tail_wing.closure_ribs[1].vertices[
    #                                                                       2].point.y)
    pt_le_y = 0
    pt_le_x = obj.def_v_tail_wing.closure_ribs[1].vertices[1].point.x
    pt_le_x = pt_le_x + v_tail_xshift(obj)
    pt_le_z = obj.def_v_tail_wing.closure_ribs[1].vertices[1].point.z + obj.cabin_diameter

    pt_te = Point(pt_te_x, pt_te_y, pt_te_z)
    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)
    return pt_te, pt_le


def section_rudder_root(obj):
    return avl.Section(le_pt=rudder_root_le_te_points(obj)[0],
                       chord=Point.distance(*rudder_root_le_te_points(obj)))


def section_rudder_tip(obj):
    return avl.Section(le_pt=rudder_tip_le_te_points(obj)[0],
                       chord=Point.distance(*rudder_tip_le_te_points(obj)))


def rudder_surface(obj):
    return avl.Surface(name="Rudder",
                       sections=[section_rudder_root(obj), section_rudder_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0,
                       angle=obj.rud_angle)


def fin_bot_root_le_te_points(obj):
    crv = obj.translate_v_tail_wing.edges[0]
    pt_te = crv.start
    pt_le = crv.extremum(pt_te, distance="max")["point"]
    return pt_le, pt_te


def fin_bot_tip_le_te_points(obj):
    crv = obj.def_v_tail_wing.fixed_part.edges[15]
    # Trailing Edge
    pt_te_x = crv.start.x + v_tail_xshift(obj)
    pt_te_y = 0
    pt_te_z = crv.start.z + obj.cabin_diameter
    pt_te = Point(pt_te_x, pt_te_y, pt_te_z)

    # Leading Edge
    crv = obj.def_v_tail_wing.fixed_part.edges[11]
    pt_le = crv.extremum(crv.start, distance="max")["point"]
    pt_le_x = pt_le.x + v_tail_xshift(obj)
    pt_le_y = 0
    pt_le_z = pt_le.z + obj.cabin_diameter
    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)
    return pt_le, pt_te


def section_fin_bot_root(obj):
    return avl.Section(le_pt=fin_bot_root_le_te_points(obj)[0],
                       chord=Point.distance(*fin_bot_root_le_te_points(obj)))


def section_fin_bot_tip(obj):
    return avl.Section(le_pt=fin_bot_tip_le_te_points(obj)[0],
                       chord=Point.distance(*fin_bot_tip_le_te_points(obj)))


def fin_bot_surface(obj):
    return avl.Surface(name="Vertical Bottom",
                       sections=[section_fin_bot_root(obj), section_fin_bot_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0)


def fin_cen_root_le_te_points(obj):
    crv = obj.def_v_tail_wing.fixed_part.edges[11]
    # Trailing Edge
    pt_te_x = crv.start.x + v_tail_xshift(obj)
    pt_te_y = 0
    pt_te_z = crv.start.z + obj.cabin_diameter
    pt_te = Point(pt_te_x, pt_te_y, pt_te_z)

    # Leading Edge
    pt_le = crv.extremum(crv.start, distance="max")["point"]
    pt_le_x = pt_le.x + v_tail_xshift(obj)
    pt_le_y = 0
    pt_le_z = pt_le.z + obj.cabin_diameter
    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)
    return pt_le, pt_te


def fin_cen_tip_le_te_points(obj):
    crv = obj.def_v_tail_wing.fixed_part.edges[3]
    # Trailing Edge
    pt_te_x = crv.start.x + v_tail_xshift(obj)
    pt_te_y = 0
    pt_te_z = crv.start.z + obj.cabin_diameter
    pt_te = Point(pt_te_x, pt_te_y, pt_te_z)

    # Leading Edge
    pt_le = crv.extremum(crv.start, distance="max")["point"]
    pt_le_x = pt_le.x + v_tail_xshift(obj)
    pt_le_y = 0
    pt_le_z = pt_le.z + obj.cabin_diameter
    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)
    return pt_le, pt_te


def section_fin_cen_root(obj):
    return avl.Section(le_pt=fin_cen_root_le_te_points(obj)[0],
                       chord=Point.distance(*fin_cen_root_le_te_points(obj)))


def section_fin_cen_tip(obj):
    return avl.Section(le_pt=fin_cen_tip_le_te_points(obj)[0],
                       chord=Point.distance(*fin_cen_tip_le_te_points(obj)))


def fin_cen_surface(obj):
    return avl.Surface(name="Vertical Centre",
                       sections=[section_fin_cen_root(obj), section_fin_cen_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0)


def fin_top_tip_le_te_points(obj):
    crv = obj.translate_v_tail_wing.edges[2]
    pt_te = crv.start
    pt_le = crv.extremum(pt_te, distance="max")["point"]
    return pt_le, pt_te


def fin_top_root_le_te_points(obj):
    # Trailing Edge
    crv = obj.def_v_tail_wing.fixed_part.edges[8]
    pt_te_x = crv.start.x + v_tail_xshift(obj)
    pt_te_y = 0
    pt_te_z = crv.start.z + obj.cabin_diameter
    pt_te = Point(pt_te_x, pt_te_y, pt_te_z)

    # Leading Edge
    crv = obj.def_v_tail_wing.fixed_part.edges[3]
    pt_le = crv.extremum(crv.start, distance="max")["point"]
    pt_le_x = pt_le.x + v_tail_xshift(obj)
    pt_le_y = 0
    pt_le_z = pt_le.z + obj.cabin_diameter
    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)
    return pt_le, pt_te


def section_fin_top_root(obj):
    return avl.Section(le_pt=fin_top_root_le_te_points(obj)[0],
                       chord=Point.distance(*fin_top_root_le_te_points(obj)))


def section_fin_top_tip(obj):
    return avl.Section(le_pt=fin_top_tip_le_te_points(obj)[0],
                       chord=Point.distance(*fin_top_tip_le_te_points(obj)))


def fin_top_surface(obj):
    return avl.Surface(name="Vertical Top",
                       sections=[section_fin_top_root(obj), section_fin_top_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0)


def geometry(obj):
    return avl.Geometry(name="Jet",
                        surfaces=[main_surface(obj),
                                  rudder_surface(obj),
                                  htp_surface(obj),
                                  fin_bot_surface(obj),
                                  fin_cen_surface(obj),
                                  fin_top_surface(obj)],
                        density=obj.rho,
                        mach_number=obj.m_cruise,
                        ref_area=obj.def_main_wing.ref_area,
                                  #(obj.def_v_tail_wing.ref_area +
                                  #obj.def_main_wing.ref_area +
                                  #obj.def_h_tail_wing.ref_area),
                        ref_chord=obj.main_root,
                        ref_span=obj.main_w_span,
                        ref_pt=Point(0, 0, 0))


def v_tail_xshift(obj):
    return -obj.h_adc_diff + (obj.def_v_tail_wing.def_vwing.w_c_tip - obj.def_v_tail_wing.def_vwing.w_c_root)
