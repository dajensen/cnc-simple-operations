#!/usr/bin/env python3

from collections import namedtuple
from .travel import retract
from .point import Cncpoint, Cncpoint3d
from .line import cut_polyline, cut_polyline3d
import math
from .arcs import move_to, set_z, arc_to_yz


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

def clear_y_ramp(rect, bottom_y_min, bottom_y_max, cutter_diameter, start_z, depth, depth_per_pass):
    cut_depth = 0
    zdiff = min(depth_per_pass, depth - cut_depth)
    while zdiff > 0:
        cut_depth = cut_depth + zdiff
        zpos = cut_depth + start_z
        proportion = cut_depth / depth
        ymin = rect.y + proportion * (bottom_y_min - rect.y)
        ymax = rect.y + rect.y_ext + proportion * (bottom_y_max - (rect.y + rect.y_ext))
        print("( zpos: {}, proportion: {}, ymin: {}, ymax: {})".format(zpos, proportion, ymin, ymax))
        rcplane = Cncrect(rect.x, ymin, rect.x_ext, ymax-ymin)
        clear_rect_on_plane(rcplane, zpos, cutter_diameter)
        zdiff = min(depth_per_pass, depth - cut_depth)
    retract(SAFE_HEIGHT)

def contour_y_ramp(rect, bottom_y_min, bottom_y_max, cutter_diameter, start_z, depth, depth_per_pass):

    rcpath = shrink_rect(rect, cutter_diameter)
    if bottom_y_min > rcpath.y + rcpath.y_ext:
        bottom_y_min = rcpath.y + rcpath.y_ext
    if bottom_y_min < rcpath.y:
        bottom_y_min = rcpath.y

    if bottom_y_max > rcpath.y + rcpath.y_ext:
        bottom_y_max = rcpath.y + rcpath.y_ext
    if bottom_y_max < rcpath.y:
        bottom_y_max = rcpath.y

    cut_depth = 0
    zdiff = min(depth_per_pass, depth - cut_depth)
    while zdiff > 0:
        cut_depth = cut_depth + zdiff
        zpos = cut_depth + start_z
        proportion = cut_depth / depth
        ymin = rcpath.y + proportion * (bottom_y_min - rcpath.y)
        ymax = rcpath.y + rcpath.y_ext + proportion * (bottom_y_max - (rcpath.y + rcpath.y_ext))
        print("( zpos: {}, proportion: {}, ymin: {}, ymax: {})".format(zpos, proportion, ymin, ymax))
        rcplane = Cncrect(rcpath.x, ymin, rcpath.x_ext, ymax-ymin)
        shrink_rect(rcplane, cutter_diameter)
        outline_rect(rcplane, zpos)
        zdiff = min(depth_per_pass, depth - cut_depth)
    retract(SAFE_HEIGHT)

def roundover(rect, radius, cutter_diameter, start_z, depth):
    # When we run this, I'm figuring that there has already been some rough clearing done, so we don't end up plunging the bit too deeply into the material
    # This method does not account for any clearing, just for trimming a square edge into a rounded one.
    # Using radians here, not degrees.
    cutter_radius = cutter_diameter / 2
    max_arc_len = cutter_diameter / 16
    stop_point = math.asin(cutter_radius / (radius + cutter_radius))                      # want to stop before doing the whole quarter circle, because that would have the tip of the bit going below the bottom of the roundover.
#    print("stop_point: {}".format(stop_point))
    total_arc_len = (math.pi / 2  - stop_point) * radius
#    print("total_arc_len: {}".format(total_arc_len))

    num_cuts = int(total_arc_len / max_arc_len) + 1
    angle_per_cut = (math.pi / 2 - stop_point) / num_cuts
#    print("num_cuts: {}, angle_per_cut: {}".format(num_cuts, angle_per_cut))

    x_ends = [rect.x + cutter_radius, rect.x + rect.x_ext - cutter_radius]
    end = 0

    set_z(SAFE_HEIGHT)
    move_to(x_ends[end], rect.y)
    move_to(x_ends[end], rect.y, start_z)

    for idx in range(num_cuts + 1):
        angle = math.pi / 2 - idx * angle_per_cut
        yloc = rect.y + radius * math.cos(angle)
        zloc = start_z - radius + radius * math.sin(angle)
        print("( angle: {}, yloc: {}, zloc: {} )".format(angle, yloc, zloc))

        # yloc and zloc are points on the circle, not the location of the tip of the cutting tool.
        # now we need to add offsets for the cutting tool so that the circle actually gets created right.
        # I'm assuming a ball end cutter here
        # theta for the cutter should be the complemetary angle for theta of the roundover
        cutter_y = cutter_radius * math.cos(angle)
        cutter_z = cutter_radius - (cutter_radius * math.sin(angle))
        print("( offset angle: {}, y offset: {}, z offset: {} )".format(angle, cutter_y, cutter_z))

        ycarve = yloc + cutter_y
        zcarve = zloc - cutter_z
#        ycarve = yloc
#        zcarve = zloc
        
#        if zcarve < start_z - depth:
#            break

        move_to(x_ends[end], ycarve, zcarve + 2)
        move_to(x_ends[end], ycarve, zcarve)

        end = not end
        move_to(x_ends[end], ycarve, zcarve)
        move_to(x_ends[end], ycarve, zcarve + 2)

    retract(SAFE_HEIGHT)
