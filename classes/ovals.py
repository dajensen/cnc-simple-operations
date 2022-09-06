#!/usr/bin/env python3

from collections import namedtuple
from .travel import retract
from .point import Cncpoint, Cncpoint3d
from .rectangles import Cncrect, generate_vertical_tab_polylines, generate_horizontal_tab_polylines, expand_rect, SAFE_HEIGHT
from .line import cut_polyline, cut_polyline3d
from .arcs import cut_arc_on_plane

Cncrect = namedtuple('Cncrect', ['x', 'y', 'x_ext', 'y_ext'])

def generate_tab_polylines(start, end, z, tab_width, bridge_z):
    if start.x == end.x:
        return generate_vertical_tab_polylines(start, end, z, tab_width, bridge_z)
    else:
        if start.y== end.y:
            return generate_horizontal_tab_polylines(start, end, z, tab_width, bridge_z)
        else:
            print("( TROUBLE!!! Tabs can currently only be added on horizontal or vertical lines. )")    
            return None

def outline_oval(rect, z):
    print("")
    print("( Outlining rect x:{} y:{} width:{} height:{} )".format(rect.x, rect.y, rect.x_ext, rect.y_ext))
    cut_polyline((Cncpoint(rect.x, rect.y),
                    Cncpoint(rect.x, rect.y + rect.y_ext), 
                    Cncpoint(rect.x + rect.x_ext, rect.y + rect.y_ext),
                    Cncpoint(rect.x + rect.x_ext, rect.y),
                    Cncpoint(rect.x, rect.y)
                    ), z)

def outline_oval_with_tabs(rect, z, tab_width, tab_depth):
    print("")
    print("( Outlining WITH TABS rect x:{} y:{} width:{} height:{} tab_height: {})".format(rect.x, rect.y, rect.x_ext, rect.y_ext, tab_depth))

    if z <= tab_depth:
        outline_oval(rect, z)
    else:
        line_series = generate_tab_polylines(Cncpoint(rect.x, rect.y), Cncpoint(rect.x, rect.y + rect.y_ext), -z, tab_width, -tab_depth)
        cut_polyline3d(line_series, z)
        line_series = generate_tab_polylines(Cncpoint(rect.x, rect.y + rect.y_ext), Cncpoint(rect.x + rect.x_ext, rect.y + rect.y_ext), -z, tab_width, -tab_depth)
        cut_polyline3d(line_series, z)
        line_series = generate_tab_polylines(Cncpoint(rect.x + rect.x_ext, rect.y + rect.y_ext), Cncpoint(rect.x + rect.x_ext, rect.y), -z, tab_width, -tab_depth)
        cut_polyline3d(line_series, z)
        line_series = generate_tab_polylines(Cncpoint(rect.x + rect.x_ext, rect.y), Cncpoint(rect.x, rect.y), -z, tab_width, -tab_depth)
        cut_polyline3d(line_series, z)

# This is an OUTER oval (cutting outside the rect provided)
def cut_oval(rect, depth, depth_per_pass, cutter_diameter):
    bigger_rect = expand_rect(rect, cutter_diameter)
    zpos = 0    # This is not correct, but it will work for now
    diff = min(depth_per_pass, depth - zpos)
#    print("( diff: {} {})".format(diff, depth + zpos))
    while diff > 0:
        zpos = zpos + diff
#        print("( zpos: {})".format(zpos))

        outline_oval(bigger_rect, zpos)        # I think we need to expand the rect by half the cutter diameter on every side, so that the outlined area is the rect we were given.
                                        # This is probably also a problem for cut_outline_with_tabs.

        diff = min(depth_per_pass, depth - zpos)
#        print("( diff: {} {})".format(diff, depth + zpos))
    retract(SAFE_HEIGHT)
 
# This is an OUTER oval (cutting outside the rect provided)
def cut_oval_with_tabs(rect, depth, depth_per_pass, cutter_diameter, tab_width, bridge_height):
    bigger_rect = expand_rect(rect, cutter_diameter)
    zpos = 0    # This is not correct, but it will work for now
    diff = min(depth_per_pass, depth - zpos)
#    print("( diff: {} {})".format(diff, depth + zpos))
    while diff > 0:
        zpos = zpos + diff
#        print("( zpos: {})".format(zpos))

        outline_oval_with_tabs(bigger_rect, zpos, cutter_diameter + tab_width, depth - bridge_height)

        diff = min(depth_per_pass, depth - zpos)
#        print("( diff: {} {})".format(diff, depth + zpos))
    retract(SAFE_HEIGHT)
