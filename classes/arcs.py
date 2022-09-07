#!/usr/bin/env python3

from collections import namedtuple
import math
import numpy as np
from .travel import retract
from .point import Cncpoint

SAFE_HEIGHT = 5

def cart2pol(x, y):
    radius = np.sqrt(x**2 + y**2)
    angle = np.arctan2(y, x)
    return(radius, angle)

def pol2cart(radius, angle):
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    return(x, y)

def comment(str = None):
    if str:
        print("( {} )".format(str))
    else:
        print("")

def move_to(x, y, z = None):
    if z == None:
        print("G01 X{:.4f} Y{:.4f}".format(x, y))
    else:
        print("G01 X{:.4f} Y{:.4f} Z{:.4f}".format(x, y, z))

def set_z(z):
        print("G01 Z{:.4f}".format(z))

def arc_to(x, y, center_x, center_y, clockwise):
    if clockwise:
        print("G02 I{:.4f} J{:.4f} X{:.4f} Y{:.4f} P1".format(center_x, center_y, x, y))
    else:
        print("G03 I{:.4f} J{:.4f} X{:.4f} Y{:.4f} P1".format(center_x, center_y, x, y))

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

def cut_circle_on_plane(center, diameter, z, steps, cutter_diameter):
    comment("Circle")
    move_to(center.x, center.y)
    set_z(z)

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

    retract(SAFE_HEIGHT)


def cut_circle(center, diameter, depth, depth_per_pass, cutter_diameter):
    print("( Cut circle )")
    zpos = 0    # This is not    diff = min(depth_per_pass, depth + zpos)
    diff = min(depth_per_pass, depth + zpos)
    while diff > 0:
        zpos = zpos - diff
        cut_circle_on_plane(center, diameter, zpos, 10, cutter_diameter)
        diff = min(depth_per_pass, depth + zpos)
