#!/usr/bin/env python3

from classes.line import cut_rotary_line
from classes.point import Cncpoint, Cncpoint4d
from classes.travel import travel_to, retract, set_depth
from classes.ambles import emit_preamble, emit_postamble

# Tool Setup
CUTTER_DIAMETER = 6.35    # it's a 1/2 mm bit
ROTATIONS_PER_SLICE = 10
SAFE_HEIGHT = 5

# Project Config
STOCK_X = 20
STOCK_A = 32
START_X = 18
END_X = 0
STEP_X = -1.5

SLOPE_RISE = -20
SLOPE_RUN = 15


emit_preamble()

x = START_X
y = 0
z = 0
a = 0

while x >= END_X:
    a = a + 360 * ROTATIONS_PER_SLICE
    travel_to(Cncpoint(x, y), SAFE_HEIGHT)
    set_depth(0)
    cut_rotary_line(Cncpoint4d(x + SLOPE_RUN, y, z + SLOPE_RISE, a))
    x += STEP_X

# Go back and do one last pass with a very fine step size to clean up the face.
x = END_X
a = a + 360 * 8 * ROTATIONS_PER_SLICE
travel_to(Cncpoint(x, y), SAFE_HEIGHT)
set_depth(0)
cut_rotary_line(Cncpoint4d(x + SLOPE_RUN, y, z + SLOPE_RISE, a))

travel_to(Cncpoint(0, 0), SAFE_HEIGHT)

emit_postamble()
