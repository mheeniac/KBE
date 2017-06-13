import parapy.lib.avl as avl
from parapy.geom import Point


def section_main_root(obj):
    """
    Define the airfoil section of the root main wing
    :rtype: avl.AirfoilCurveSection
    """
    return avl.AirfoilCurveSection(curve_in=obj.main_wing[0].edges[0])


def section_main_tip(obj):
    """
    Define the airfoil section of the tip of the main wing
    :rtype: avl.AirfoilCurveSection
    """
    return avl.AirfoilCurveSection(curve_in=obj.main_wing[0].edges[2])


def main_surface(obj):
    """
    Generate the surface for the main wing consisting of the two airfoils
    :rtype: avl.Surface
    """
    return avl.Surface(name="Main Wing",
                       sections=[section_main_root(obj), section_main_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0,
                       y_duplicate=0.0)


def section_htp_root(obj):
    """
    Define the airfoil section of the root of the horizontal wing
    :rtype: avl.AirfoilCurveSection
    """
    return avl.AirfoilCurveSection(curve_in=obj.translate_h_tail_wing[0].edges[0])


def section_htp_tip(obj):
    """
    Define the airfoil section of the tip of the horizontal wing
    :rtype: avl.AirfoilCurveSection
    """
    return avl.AirfoilCurveSection(curve_in=obj.translate_h_tail_wing[0].edges[2])


def htp_surface(obj):
    """
    Generate the surface for the horizontal tail wing consisting of the two airfoils
    :rtype: avl.Surface
    """
    return avl.Surface(name="HTP",
                       sections=[section_htp_root(obj), section_htp_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0,
                       y_duplicate=0.0)


def rudder_root_le_te_points(obj):
    """
    This defines the leading edge and the trailing edge points of the moving rudder part root
    :rtype: avl.tuple[Points]
    """
    # Trailing Edge
    pt_te = obj.fixed_v_wing[1].vertices[11].point

    # Leading Edge
    pt_le_y = 0
    pt_le_x = obj.fixed_v_wing[1].vertices[7].point.x  # X point
    pt_le_z = obj.fixed_v_wing[1].vertices[7].point.z  # Z point plus shift

    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)  # Create point type
    return pt_le, pt_te  # Return in tuple


def rudder_tip_le_te_points(obj):
    """
    This defines the leading edge and the trailing edge points of the moving rudder part tip
    :rtype: avl.tuple[Points]
    """
    # Trailing Edge
    pt_te_x = obj.def_v_tail_wing.closure_ribs[1].vertices[0].point.x  # X point
    pt_te_x = pt_te_x  # Shift the x point
    pt_te_y = 0
    pt_te_z = obj.def_v_tail_wing.closure_ribs[1].vertices[0].point.z  # Z point plus shift

    # Leading Edge
    pt_le_y = 0
    pt_le_x = obj.def_v_tail_wing.closure_ribs[1].vertices[1].point.x  # X point
    pt_le_x = pt_le_x  # Shift the x point
    pt_le_z = obj.def_v_tail_wing.closure_ribs[1].vertices[1].point.z  # Z point plus shift

    pt_te = Point(pt_te_x, pt_te_y, pt_te_z)  # Create point type
    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)  # Create point type
    return pt_te, pt_le  # Return in tuple


def section_rudder_root(obj):
    """
    Create the rudder root section from the le and te te points and its length
    :rtype: avl.Section
    """
    return avl.Section(le_pt=rudder_root_le_te_points(obj)[0],
                       chord=Point.distance(*rudder_root_le_te_points(obj)))


def section_rudder_tip(obj):
    """
    Create the rudder tip section from the le and te te points and its length
    :rtype: avl.Section
    """
    return avl.Section(le_pt=rudder_tip_le_te_points(obj)[0],
                       chord=Point.distance(*rudder_tip_le_te_points(obj)))


def rudder_surface(obj):
    """
    Create the rudder surface from the root and tip sections and rotate it
    :rtype: avl.Surface
    """
    return avl.Surface(name="Rudder",
                       sections=[section_rudder_root(obj), section_rudder_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0,
                       angle=obj.rud_angle)


def fin_bot_root_le_te_points(obj):
    """
    Define the root le and te points of the fixed section under the rudder
    :rtype: avl.tuple[points]
    """
    crv = obj.def_v_tail_wing.trans_vwing.edges[0]
    pt_te = crv.start
    pt_le = crv.midpoint
    return pt_le, pt_te


def fin_bot_tip_le_te_points(obj):
    """
     Define the tip le and te points of the fixed section under the rudder
    :rtype: avl.tuple[points] 
    """
    # Trailing Edge
    pt_te = obj.fixed_v_wing[1].vertices[11].point

    # Leading Edge
    crv = obj.def_v_tail_wing.fixed_part.edges[11]
    pt_le = crv.extremum(crv.start, distance="max")["point"]
    pt_le_x = pt_le.x
    pt_le_y = 0
    pt_le_z = pt_le.z
    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)
    return pt_le, pt_te


def section_fin_bot_root(obj):
    """
    Create the fixed section under the rudder from the le and te te points and its length
    :rtype: avl.Section
    """
    return avl.Section(le_pt=fin_bot_root_le_te_points(obj)[0],
                       chord=Point.distance(*fin_bot_root_le_te_points(obj)))


def section_fin_bot_tip(obj):
    """
    Create the fixed section under the rudder from the le and te te points and its length
    :rtype: avl.Section
    """
    return avl.Section(le_pt=fin_bot_tip_le_te_points(obj)[0],
                       chord=Point.distance(*fin_bot_tip_le_te_points(obj)))


def fin_bot_surface(obj):
    """
    Create the surface of the bottom part of the fixed fin
    :rtype: avl.Surface
    """
    return avl.Surface(name="Vertical Bottom",
                       sections=[section_fin_bot_root(obj), section_fin_bot_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0)


def fin_cen_root_le_te_points(obj):
    """
     Define the root le and te points of the fixed fin center section (without rudder)
    :rtype: avl.tuple[points] 
    """
    crv = obj.def_v_tail_wing.fixed_part.edges[11]
    # Trailing Edge
    pt_te_x = crv.start.x
    pt_te_y = 0
    pt_te_z = crv.start.z
    pt_te = Point(pt_te_x, pt_te_y, pt_te_z)

    # Leading Edge
    pt_le = crv.extremum(crv.start, distance="max")["point"]
    pt_le_x = pt_le.x
    pt_le_y = 0
    pt_le_z = pt_le.z
    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)
    return pt_le, pt_te


def fin_cen_tip_le_te_points(obj):
    """
     Define the tip le and te points of the fixed fin center section (without rudder)
    :rtype: avl.tuple[points] 
    """
    crv = obj.def_v_tail_wing.fixed_part.edges[3]
    # Trailing Edge
    pt_te_x = crv.start.x
    pt_te_y = 0
    pt_te_z = crv.start.z
    pt_te = Point(pt_te_x, pt_te_y, pt_te_z)

    # Leading Edge
    crv = obj.fixed_v_wing[1].edges[9]
    pt_le = crv.extremum(crv.start, distance="max")["point"]
    pt_le_x = pt_le.x
    pt_le_y = 0
    pt_le_z = pt_le.z
    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)
    return pt_le, pt_te


def section_fin_cen_root(obj):
    """
    Create root section of the fixed fin center
    :rtype: avl.Section
    """
    return avl.Section(le_pt=fin_cen_root_le_te_points(obj)[0],
                       chord=Point.distance(*fin_cen_root_le_te_points(obj)))


def section_fin_cen_tip(obj):
    """
    Create tip section of the fixed fin center
    :rtype: avl.Section
    """
    return avl.Section(le_pt=fin_cen_tip_le_te_points(obj)[0],
                       chord=Point.distance(*fin_cen_tip_le_te_points(obj)))


def fin_cen_surface(obj):
    """
    Create the fixed fin center part surface
    :rtype: avl.Surface
    """
    return avl.Surface(name="Vertical Centre",
                       sections=[section_fin_cen_root(obj), section_fin_cen_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0)


def fin_top_tip_le_te_points(obj):
    """
     Define the tip le and te points of the fixed fin top section (without rudder)
    :rtype: avl.tuple[points] 
    """
    crv = obj.fixed_v_wing[1].edges[8]
    pt_te = obj.fixed_v_wing[1].vertices[0].point
    pt_le = crv.extremum(pt_te, distance="max")["point"]
    return pt_le, pt_te


def fin_top_root_le_te_points(obj):
    """
     Define the root le and te points of the fixed fin top section (without rudder)
    :rtype: avl.tuple[points] 
    """
    # Trailing Edge
    pt_te = obj.fixed_v_wing[1].vertices[4].point

    # Leading Edge
    crv = obj.fixed_v_wing[1].edges[9]
    pt_le = crv.extremum(crv.start, distance="max")["point"]
    pt_le_x = pt_le.x
    pt_le_y = 0
    pt_le_z = pt_le.z
    pt_le = Point(pt_le_x, pt_le_y, pt_le_z)
    return pt_le, pt_te


def section_fin_top_root(obj):
    """
    Create root section of the fixed fin top
    :rtype: avl.Section
    """
    return avl.Section(le_pt=fin_top_root_le_te_points(obj)[0],
                       chord=Point.distance(*fin_top_root_le_te_points(obj)))


def section_fin_top_tip(obj):
    """
    Create tip section of the fixed fin top
    :rtype: avl.Section
    """
    return avl.Section(le_pt=fin_top_tip_le_te_points(obj)[0],
                       chord=Point.distance(*fin_top_tip_le_te_points(obj)))


def fin_top_surface(obj):
    """
    Create the fixed fin top part surface
    :rtype: avl.Surface
    """
    return avl.Surface(name="Vertical Top",
                       sections=[section_fin_top_root(obj), section_fin_top_tip(obj)],
                       n_chord=10,
                       c_spacing=0.0,
                       n_span=5,
                       s_spacing=0.0)


def geometry(obj):
    """
    Combine all the surfaces into a geometry. For the reference area the main wing ref area is used. It is important to
    use this area when performing any future calculations!
    :rtype: avl.Geometry
    """
    return avl.Geometry(name="Jet",
                        surfaces=[main_surface(obj),
                                  rudder_surface(obj),
                                  htp_surface(obj),
                                  fin_bot_surface(obj),
                                  fin_cen_surface(obj),
                                  fin_top_surface(obj),
                                  ],
                        density=obj.rho,
                        mach_number=obj.m_cruise,
                        ref_area=obj.w_c_root * obj.w_span,
                        ref_chord=obj.w_c_root,
                        ref_span=obj.w_span * 2,
                        ref_pt=Point(0, 0, 0))
