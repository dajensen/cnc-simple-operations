#!/usr/bin/env python3

from collections import namedtuple
import numpy as np
from .travel import retract
from .point import Cncpoint

SAFE_HEIGHT = 5

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
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

    rho, phi_start = cart2pol(start.x - center.x, start.y - center.y)
    rho, phi_end = cart2pol(end.x - center.x, end.y - center.y)
    radius_this_pass = rho + cutter_diameter / 2
    outer_radius = radius_this_pass + arc_width - cutter_diameter

    diff = min(cutter_diameter / 2, outer_radius - radius_this_pass)

    while diff > 0:
        start_x_offset, start_y_offset = pol2cart(radius_this_pass, phi_start)
        end_x_offset, end_y_offset = pol2cart(radius_this_pass, phi_end)
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

