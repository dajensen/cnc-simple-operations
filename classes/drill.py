#!/usr/bin/env python3

from collections import namedtuple
import math
from .travel import retract
from .point import Cncpoint
from .line import comment
from .arcs import move_to, set_z, SAFE_HEIGHT

def drill_to(x, y, z, feedrate):
    print("G01 X{:.6f} Y{:.6f} Z{:.6f} F{:.0f}".format(x, y, z, feedrate))


def peckdrill(center, start_z, depth, depth_per_pass, retract_height, feed_rate):
 
    comment()
    comment("Peck drill")
    move_to(center.x, center.y, SAFE_HEIGHT)

    drill_depth = start_z
    move_to(center.x, center.y, -drill_depth)
    while drill_depth < start_z + depth:
        drill_depth = min(drill_depth + depth_per_pass, start_z + depth)
        drill_to(center.x, center.y, -drill_depth, feed_rate)
        set_z(retract_height)
    
    retract(SAFE_HEIGHT)
