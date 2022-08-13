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


def gcode_arc(start, center, z, end=None):
    if end == None:
        end = start
    print("")
    print("G01 X{:.4f} Y{:.4f}".format(start.x, start.y))
    print("G01 Z{:.4f}".format(z))
    print("G02 I{:.4f} J{:.4f} X{:.4f} Y{:.4f}".format(center.x - start.x, center.y - start.y, end.x, end.y))
    retract(SAFE_HEIGHT)

def cut_arc_on_plane(arc_width, start, center, z, cutter_diameter, end=None):
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
        gcode_arc(Cncpoint(center.x + start_x_offset, center.y + start_y_offset), center, z, Cncpoint(center.x + end_x_offset, center.y + end_y_offset))
        diff = min(cutter_diameter / 2, outer_radius - radius_this_pass)
        radius_this_pass += diff
    
def cut_arc(arc_width, start, center, cutter_diameter, depth, depth_per_pass, end=None):
    zpos = 0    # This is not correct, but it will work for now
    diff = min(depth_per_pass, depth + zpos)
    while diff > 0:
        zpos = zpos - diff
        cut_arc_on_plane(arc_width, start, center, zpos, cutter_diameter, end)
        diff = min(depth_per_pass, depth + zpos)

def cut_circle_on_plane(center, diameter, z, steps, cutter_diameter):
    radius_increment = cutter_diameter / steps
    angle_increment = -2*math.pi / steps
    radius = radius_increment
    angle = 0

    x, y = pol2cart(radius, angle)
    print("")
    print("G01 X{:.4f} Y{:.4f}".format(center.x, center.y))
    print("G01 Z{:.4f}".format(z))

    print("G91 ( relative mode)")

    while radius <= diameter / 2 - cutter_diameter / 2:
        last_x = x
        last_y = y
        angle += angle_increment
        radius += radius_increment
        x, y = pol2cart(radius, angle)
        print("G02 X{:.4f} Y{:.4f} R{:.4f}".format(x - last_x, y - last_y, radius))

    print("G90 ( back to absolute mode)")
    # Calculate the point where we should currently be (in case of any accumulated error during the relative motion)
    x, y = pol2cart(radius, angle)
    x += center.x
    y += center.y
    print("G01 X{:.4f} Y{:.4f}".format(x, y))

    # Do half a circle around the outside edge
    angle += math.pi
    x, y = pol2cart(radius, angle)
    x += center.x
    y += center.y
    print("G02 I{:.4f} J{:.4f} X{:.4f} Y{:.4f} P1".format(x - center.x, y - center.y, x, y))

    # do the other half of the circle
    angle += math.pi
    x, y = pol2cart(radius, angle)
    x += center.x
    y += center.y
    print("G02 I{:.4f} J{:.4f} X{:.4f} Y{:.4f} P1".format(x - center.x, y - center.y, x, y))

    retract(SAFE_HEIGHT)


def cut_circle(center, diameter, depth, depth_per_pass, cutter_diameter):
    print("( Cut circle )")
    zpos = 0    # This is not    diff = min(depth_per_pass, depth + zpos)
    diff = min(depth_per_pass, depth + zpos)
    while diff > 0:
        zpos = zpos - diff
        cut_circle_on_plane(center, diameter, zpos, 10, cutter_diameter)
        diff = min(depth_per_pass, depth + zpos)
