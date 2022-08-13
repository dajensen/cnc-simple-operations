#!/usr/bin/env python3

from collections import namedtuple
from .travel import retract
from .point import Cncpoint, Cncpoint3d
from .line import cut_polyline, cut_polyline3d


SAFE_HEIGHT = 5

Cncrect = namedtuple('Cncrect', ['x', 'y', 'x_ext', 'y_ext'])
#outer = Cncrect(5, 10, 30, 40)
#print("Outer x:{} y:{} x_ext:{} y_ext{}".format(outer.x, outer.y, outer.x_ext, outer.y_ext))

def zigzag_tall(rect, step_amount):
    bottom = rect.y
    xpos = rect.x
    top = rect.y + rect.y_ext
    while(xpos < rect.x + rect.x_ext):
        xpos  = xpos + min(step_amount / 2, rect.x + rect.x_ext - xpos)
        print("G01 X{:.4f} Y{:.4f}".format(xpos, bottom)) # to the bottom
        xpos  = xpos + min(step_amount / 2, rect.x + rect.x_ext - xpos)
        print("G01 X{:.4f} Y{:.4f}".format(xpos, top)) # back to the top

def zigzag_wide(rect, step_amount):
    ypos = rect.y
    left = rect.x
    right = rect.x + rect.x_ext
    while(ypos < rect.y + rect.y_ext):
        ypos  = ypos + min(step_amount / 2, rect.y + rect.y_ext - ypos)
        print("G01 X{:.4f} Y{:.4f}".format(left, ypos)) # to the left
        ypos  = ypos + min(step_amount / 2, rect.y + rect.y_ext - ypos)
        print("G01 X{:.4f} Y{:.4f}".format(right, ypos)) # back to the right

def hog_center(rect, z, step_amount):
    print("")
    print("( Hogging rect x:{} y:{} width:{} height:{} )".format(rect.x, rect.y, rect.x_ext, rect.y_ext))
    print("G01 X{:.4f} Y{:.4f}".format(rect.x, rect.y))
    print("G01 Z{:.4f}".format(-z))
    print("G01 X{:.4f} Y{:.4f}".format(rect.x + rect.x_ext, rect.y))
    if rect.x_ext > rect.y_ext:
        zigzag_wide(rect, step_amount)
    else:
        zigzag_tall(rect, step_amount)
    print("G01 X{:.4f} Y{:.4f}".format(rect.x, rect.y + rect.y_ext))   # finish on the left

def outline_rect(rect, z):
    print("")
    print("( Outlining rect x:{} y:{} width:{} height:{} )".format(rect.x, rect.y, rect.x_ext, rect.y_ext))
    cut_polyline((Cncpoint(rect.x, rect.y),
                    Cncpoint(rect.x, rect.y + rect.y_ext), 
                    Cncpoint(rect.x + rect.x_ext, rect.y + rect.y_ext),
                    Cncpoint(rect.x + rect.x_ext, rect.y),
                    Cncpoint(rect.x, rect.y)
                    ), z)

def generate_vertical_tab_polylines(start, end, z, tab_width, bridge_z):
    rv = []
    center_y = (start.y + end.y) / 2
    rv.append(Cncpoint3d(start.x, start.y, z))
    if start.y < end.y:
        rv.append(Cncpoint3d(start.x, center_y - tab_width / 2, z))
        rv.append(Cncpoint3d(start.x, center_y - tab_width / 2, bridge_z))
        rv.append(Cncpoint3d(start.x, center_y + tab_width / 2, bridge_z))
        rv.append(Cncpoint3d(start.x, center_y + tab_width / 2, z))
    else:
        rv.append(Cncpoint3d(start.x, center_y + tab_width / 2, z))
        rv.append(Cncpoint3d(start.x, center_y + tab_width / 2, bridge_z))
        rv.append(Cncpoint3d(start.x, center_y - tab_width / 2, bridge_z))
        rv.append(Cncpoint3d(start.x, center_y - tab_width / 2, z))

    rv.append(Cncpoint3d(end.x, end.y, z))
    return rv

def generate_horizontal_tab_polylines(start, end, z, tab_width, bridge_z):
    rv = []
    center_x = (start.x + end.x) / 2
    rv.append(Cncpoint3d(start.x, start.y, z))
    if start.x < end.x:
        rv.append(Cncpoint3d(center_x - tab_width / 2, start.y, z))
        rv.append(Cncpoint3d(center_x - tab_width / 2, start.y, bridge_z))
        rv.append(Cncpoint3d(center_x + tab_width / 2, start.y, bridge_z))
        rv.append(Cncpoint3d(center_x + tab_width / 2, start.y, z))
    else:
        rv.append(Cncpoint3d(center_x + tab_width / 2, start.y, z))
        rv.append(Cncpoint3d(center_x + tab_width / 2, start.y, bridge_z))
        rv.append(Cncpoint3d(center_x - tab_width / 2, start.y, bridge_z))
        rv.append(Cncpoint3d(center_x - tab_width / 2, start.y, z))

    rv.append(Cncpoint3d(end.x, end.y, z))
    return rv

def generate_tab_polylines(start, end, z, tab_width, bridge_z):
    if start.x == end.x:
        return generate_vertical_tab_polylines(start, end, z, tab_width, bridge_z)
    else:
        if start.y== end.y:
            return generate_horizontal_tab_polylines(start, end, z, tab_width, bridge_z)
        else:
            print("( TROUBLE!!! Tabs can currently only be added on horizontal or vertical lines. )")    
            return None

def outline_with_tabs(rect, z, tab_width, tab_depth):
    print("")
    print("( Outlining WITH TABS rect x:{} y:{} width:{} height:{} tab_height: {})".format(rect.x, rect.y, rect.x_ext, rect.y_ext, tab_depth))

    if z <= tab_depth:
        outline_rect(rect, z)
    else:
        line_series = generate_tab_polylines(Cncpoint(rect.x, rect.y), Cncpoint(rect.x, rect.y + rect.y_ext), -z, tab_width, -tab_depth)
        cut_polyline3d(line_series, z)
        line_series = generate_tab_polylines(Cncpoint(rect.x, rect.y + rect.y_ext), Cncpoint(rect.x + rect.x_ext, rect.y + rect.y_ext), -z, tab_width, -tab_depth)
        cut_polyline3d(line_series, z)
        line_series = generate_tab_polylines(Cncpoint(rect.x + rect.x_ext, rect.y + rect.y_ext), Cncpoint(rect.x + rect.x_ext, rect.y), -z, tab_width, -tab_depth)
        cut_polyline3d(line_series, z)
        line_series = generate_tab_polylines(Cncpoint(rect.x + rect.x_ext, rect.y), Cncpoint(rect.x, rect.y), -z, tab_width, -tab_depth)
        cut_polyline3d(line_series, z)


def shrink_rect(rect, shrink_amount):
    if rect.x_ext - shrink_amount <= 0 or rect.y_ext - shrink_amount <= 0:
        return None
    return Cncrect(rect.x + shrink_amount / 2, rect.y + shrink_amount / 2, rect.x_ext - shrink_amount, rect.y_ext - shrink_amount)

def expand_rect(rect, expand_amount):
    if rect.x_ext - expand_amount <= 0 or rect.y_ext - expand_amount <= 0:
        return None
    return Cncrect(rect.x - expand_amount / 2, rect.y - expand_amount / 2, rect.x_ext + expand_amount, rect.y_ext + expand_amount)

def clear_rect_on_plane(rect, z, cutter_diameter):
    hogrect = shrink_rect(rect, cutter_diameter * 2)
    if hogrect:
        hog_center(hogrect, z, cutter_diameter / 2)
    outlinerect = shrink_rect(rect, cutter_diameter)
    if outlinerect:
        outline_rect(outlinerect, z)

    
def clear_rect(rect, cutter_diameter, depth, depth_per_pass):
    zpos = 0    # This is not correct, but it will work for now
    diff = min(depth_per_pass, depth - zpos)
#    print("( diff: {} {})".format(diff, depth + zpos))
    while diff > 0:
        zpos = zpos + diff
#        print("( zpos: {})".format(zpos))
        clear_rect_on_plane(rect, zpos, cutter_diameter)
        diff = min(depth_per_pass, depth - zpos)
#        print("( diff: {} {})".format(diff, depth + zpos))
    retract(SAFE_HEIGHT)

def cut_outline(rect, depth, depth_per_pass, cutter_diameter):
    bigger_rect = expand_rect(rect, cutter_diameter)
    zpos = 0    # This is not correct, but it will work for now
    diff = min(depth_per_pass, depth - zpos)
#    print("( diff: {} {})".format(diff, depth + zpos))
    while diff > 0:
        zpos = zpos + diff
#        print("( zpos: {})".format(zpos))

        outline_rect(bigger_rect, zpos)        # I think we need to expand the rect by half the cutter diameter on every side, so that the outlined area is the rect we were given.
                                        # This is probably also a problem for cut_outline_with_tabs.

        diff = min(depth_per_pass, depth - zpos)
#        print("( diff: {} {})".format(diff, depth + zpos))
    retract(SAFE_HEIGHT)
 
def cut_outline_with_tabs(rect, depth, depth_per_pass, cutter_diameter, tab_width, bridge_height):
    bigger_rect = expand_rect(rect, cutter_diameter)
    zpos = 0    # This is not correct, but it will work for now
    diff = min(depth_per_pass, depth - zpos)
#    print("( diff: {} {})".format(diff, depth + zpos))
    while diff > 0:
        zpos = zpos + diff
#        print("( zpos: {})".format(zpos))

        outline_with_tabs(bigger_rect, zpos, cutter_diameter + tab_width, depth - bridge_height)

        diff = min(depth_per_pass, depth - zpos)
#        print("( diff: {} {})".format(diff, depth + zpos))
    retract(SAFE_HEIGHT)

