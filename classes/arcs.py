#!/usr/bin/env python3

from collections import namedtuple
import math
import numpy as np
from .travel import retract
from .point import Cncpoint
from .line import comment

SAFE_HEIGHT = 5

def cart2pol(x, y):
    radius = np.sqrt(x**2 + y**2)
    angle = np.arctan2(y, x)
    return(radius, angle)

def pol2cart(radius, angle):
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    return(x, y)

def move_to(x, y, z = None):
    if z == None:
        print("G01 X{:.6f} Y{:.6f}".format(x, y))
    else:
        print("G01 X{:.6f} Y{:.6f} Z{:.6f}".format(x, y, z))

def set_z(z):
        print("G00 Z{:.6f}".format(z))

def arc_to(x, y, center_x, center_y, clockwise):
    if clockwise:
        print("G02 I{:.6f} J{:.6f} X{:.6f} Y{:.6f}".format(center_x, center_y, x, y))
    else:
        print("G03 I{:.6f} J{:.6f} X{:.6f} Y{:.6f}".format(center_x, center_y, x, y))

# an arc in the yz plane
def arc_to_yz(y, z, center_y, center_z, clockwise):
    print ("G19 ( arcs in YZ plane )")
    if clockwise:
        print("G02 J{:.6f} K{:.6f} Y{:.6f} Z{:.6f}".format(center_y, center_z, y, z))
    else:
        print("G03 J{:.6f} K{:.6f} Y{:.6f} Z{:.6f}".format(center_y, center_z, y, z))
    print ("G17 ( back to default arcs in XY plane )")

def gcode_arc(start, center, end, z, clockwise):
    if end == None:
        end = start
    comment()
    move_to(start.x, start.y)
    set_z(-z)
    arc_to(end.x, end.y, center.x, center.y, clockwise)
    retract(SAFE_HEIGHT)

def cut_arc_on_plane(arc_width, start, center, z, cutter_diameter, end, clockwise):
    if end == None:
        end = start

    radius, angle_start = cart2pol(start.x - center.x, start.y - center.y)
    radius, angle_end = cart2pol(end.x - center.x, end.y - center.y)
    radius_this_pass = radius + cutter_diameter / 2
    outer_radius = radius_this_pass + arc_width - cutter_diameter

    diff = min(cutter_diameter / 2, outer_radius - radius_this_pass)

    while diff > 0:
        start_x_offset, start_y_offset = pol2cart(radius_this_pass, angle_start)
        end_x_offset, end_y_offset = pol2cart(radius_this_pass, angle_end)
        gcode_arc(Cncpoint(center.x + start_x_offset, center.y + start_y_offset), center, Cncpoint(center.x + end_x_offset, center.y + end_y_offset), z, clockwise)
        diff = min(cutter_diameter / 2, outer_radius - radius_this_pass)
        radius_this_pass += diff
    
def cut_arc(arc_width, start, center, cutter_diameter, depth, depth_per_pass, end, clockwise):
    zpos = 0    # This is not correct, but it will work for now
    diff = min(depth_per_pass, depth + zpos)
    while diff > 0:
        zpos = zpos - diff
        cut_arc_on_plane(arc_width, start, center, zpos, cutter_diameter, end, clockwise)
        diff = min(depth_per_pass, depth + zpos)

def cut_circle_on_plane(center, diameter, z, cutter_diameter):
    comment("Circle")
    move_to(center.x, center.y)
    set_z(-z)

    prevradius = 0
    radius = cutter_diameter / 4
    sign = 1

    while radius <= diameter / 2 - cutter_diameter / 2:
        arc_to(center.x + sign * radius, center.y, sign * (radius + prevradius)/2, 0, True)
        prevradius = radius
        radius += cutter_diameter / 4
        sign = sign * -1

    # Do the outside edge
    radius = diameter / 2 - cutter_diameter / 2
    for n in range(3):
        arc_to(center.x + sign * radius, center.y, sign * (radius + prevradius)/2, 0, True)
        prevradius = radius    
        sign = sign * -1


def cut_circle(center, diameter, start_z, depth, depth_per_pass, cutter_diameter):
    comment()
    comment("Cut circle")
    zpos = start_z
    while zpos < start_z + depth:
        zpos = min(zpos + depth_per_pass, start_z + depth)
        cut_circle_on_plane(center, diameter, zpos, cutter_diameter)

    retract(SAFE_HEIGHT)
