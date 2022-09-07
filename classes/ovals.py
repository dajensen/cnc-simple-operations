#!/usr/bin/env python3

from collections import namedtuple
from .travel import retract
from .point import Cncpoint, Cncpoint3d
from .rectangles import Cncrect, generate_vertical_tab_polylines, generate_horizontal_tab_polylines, expand_rect, SAFE_HEIGHT
from .line import cut_polyline, cut_polyline3d
from .arcs import cut_arc_on_plane, move_to, arc_to

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

def outline_oval(rect, rounded_x, z):
    print("")
    print("( Outlining oval with rect x:{} y:{} width:{} height:{} )".format(rect.x, rect.y, rect.x_ext, rect.y_ext))

    if(rounded_x):
        radius = rect.x_ext / 2
        move_to(rect.x, rect.y + radius, z)
        move_to(rect.x, rect.y + rect.y_ext - radius)
        arc_to(rect.x + rect.x_ext, rect.y + rect.y_ext - radius, radius, 0, True)
        move_to(rect.x + rect.x_ext, rect.y + radius)
        arc_to(rect.x, rect.y + radius, -radius, 0, True)
    else:
        radius = rect.y_ext / 2
        move_to(rect.x + radius, rect.y, z)
        arc_to(rect.x + radius, rect.y + rect.y_ext, 0, radius, True)
        move_to(rect.x + rect.x_ext - radius, rect.y + rect.y_ext)
        arc_to(rect.x + rect.x_ext - radius, rect.y, 0, -radius, True)
        move_to(rect.x + radius, rect.y)

def outline_oval_with_tabs(rect, rounded_x, z, tab_width, tab_depth):
    print("")
    print("( Outlining oval WITH TABS rect x:{} y:{} width:{} height:{} tab_height: {})".format(rect.x, rect.y, rect.x_ext, rect.y_ext, tab_depth))

    if z >= -tab_depth:
        outline_oval(rect, rounded_x, z)
    else:
 #       line_series = generate_tab_polylines(Cncpoint(rect.x, rect.y), Cncpoint(rect.x, rect.y + rect.y_ext), -z, tab_width, -tab_depth)
 #       cut_polyline3d(line_series, z)
        if(rounded_x):
            radius = rect.x_ext / 2
            move_to(rect.x, rect.y + radius, z)
            # move_to(rect.x, rect.y + rect.y_ext - radius)
            line_series = generate_tab_polylines(Cncpoint(rect.x, rect.y + radius), Cncpoint(rect.x, rect.y + rect.y_ext - radius), z, tab_width, -tab_depth)
            cut_polyline3d(line_series, z)
            arc_to(rect.x + rect.x_ext, rect.y + rect.y_ext - radius, radius, 0, True)
            # move_to(rect.x + rect.x_ext, rect.y + radius)
            line_series = generate_tab_polylines(Cncpoint(rect.x + rect.x_ext, rect.y + rect.y_ext - radius), Cncpoint(rect.x + rect.x_ext, rect.y + radius), z, tab_width, -tab_depth)
            cut_polyline3d(line_series, z)
            arc_to(rect.x, rect.y + radius, -radius, 0, True)
        else:
            radius = rect.y_ext / 2
            move_to(rect.x + radius, rect.y, z)
            arc_to(rect.x + radius, rect.y + rect.y_ext, 0, radius, True)
            # move_to(rect.x + rect.x_ext - radius, rect.y + rect.y_ext)
            line_series = generate_tab_polylines(Cncpoint(rect.x + radius, rect.y + rect.y_ext), Cncpoint(rect.x + rect.x_ext - radius, rect.y + rect.y_ext), z, tab_width, -tab_depth)
            cut_polyline3d(line_series, z)
            arc_to(rect.x + rect.x_ext - radius, rect.y, 0, -radius, True)
            # move_to(rect.x + radius, rect.y)
            line_series = generate_tab_polylines(Cncpoint(rect.x + rect.x_ext - radius, rect.y), Cncpoint(rect.x + radius, rect.y), z, tab_width, -tab_depth)
            cut_polyline3d(line_series, z)

# This should be an INNER cleared oval (cutting inside the rect provided)
# NOT properly implemented yet - it's just outlining OUTSIDE the oval.
def cut_oval(rect, rounded_x, depth, depth_per_pass, cutter_diameter):
    bigger_rect = expand_rect(rect, cutter_diameter)
    zpos = 0    # This is not correct, but it will work for now
    diff = min(depth_per_pass, depth - zpos)
#    print("( diff: {} {})".format(diff, depth + zpos))

    if(rounded_x):
        move_to(bigger_rect.x, bigger_rect.y + bigger_rect.x_ext / 2, 0)
    else:
        move_to(bigger_rect.x + bigger_rect.y_ext / 2, bigger_rect.y, 0)

    while diff > 0:
        zpos = zpos + diff
#        print("( zpos: {})".format(zpos))

        outline_oval(bigger_rect, rounded_x, zpos)

        diff = min(depth_per_pass, depth - zpos)
#        print("( diff: {} {})".format(diff, depth + zpos))
    retract(SAFE_HEIGHT)
 
# This is an OUTER oval (cutting outside the rect provided)
def cut_oval_with_tabs(rect, rounded_x, depth, depth_per_pass, cutter_diameter, tab_width, bridge_height):
    bigger_rect = expand_rect(rect, cutter_diameter)
    zpos = 0    # This is not correct, but it will work for now
    diff = min(depth_per_pass, depth - zpos)
#    print("( diff: {} {})".format(diff, depth + zpos))

    if(rounded_x):
        move_to(bigger_rect.x, bigger_rect.y + bigger_rect.x_ext / 2, SAFE_HEIGHT)
    else:
        move_to(bigger_rect.x + bigger_rect.y_ext / 2, bigger_rect.y, SAFE_HEIGHT)

    while diff > 0:
        zpos = zpos + diff
        print("( zpos: {})".format(zpos))


        outline_oval_with_tabs(bigger_rect, rounded_x, -zpos, cutter_diameter + tab_width, depth - bridge_height)

        diff = min(depth_per_pass, depth - zpos)
#        print("( diff: {} {})".format(diff, depth + zpos))
    retract(SAFE_HEIGHT)
