#!/usr/bin/env python3

from classes.rectangles import clear_rect, Cncrect
from classes.arcs import cut_arc, Cncpoint
from classes.ambles import emit_preamble, emit_postamble

# Tool Setup
STOCK_THICKNESS = 25.4 / 2
CUTTER_DIAMETER = 25.4 / 8    # it's a 1/8" bit
DEPTH_PER_PASS = 4

# Project Config
INNER_RADIUS = 130 / 2
ARC_WIDTH = 25.4/4
CENTER_X = 0
CENTER_Y = 0
BODY_DIAMETER = 130
TOP_THICKNESS = 12.7
WALL_DEPTH = 6.5
WALL_THICKNESS = 6.75
WALL_LENGTH = 65 + 2 * (25.4/4)
PLASTIC_THICKNESS = 25.4/8 + .01   # Add just enough width that roundoff errors won't keep the cutter from fitting
CUTOUT_WIDTH = 6.35
BACK_OFFSET = 3
SIDE_OVERLAP = 2
TOUCH_SENSOR_SIZE = 55


emit_preamble()

cut_arc(PLASTIC_THICKNESS,  Cncpoint(-41.85, -39.5), Cncpoint(CENTER_X, CENTER_Y), CUTTER_DIAMETER, WALL_DEPTH, DEPTH_PER_PASS, Cncpoint(41.85, -39.5))

# Left slot
clear_rect(Cncrect(-WALL_LENGTH/2 - WALL_THICKNESS + SIDE_OVERLAP, -WALL_LENGTH/2-BACK_OFFSET, WALL_THICKNESS, WALL_LENGTH), CUTTER_DIAMETER, WALL_DEPTH, DEPTH_PER_PASS)

# Top slot
clear_rect(Cncrect(-WALL_LENGTH/2, WALL_LENGTH/2-WALL_THICKNESS - BACK_OFFSET, WALL_LENGTH, WALL_THICKNESS), CUTTER_DIAMETER, WALL_DEPTH, DEPTH_PER_PASS)

# Right slot
clear_rect(Cncrect(WALL_LENGTH/2 - SIDE_OVERLAP, -WALL_LENGTH/2-BACK_OFFSET, WALL_THICKNESS, WALL_LENGTH), CUTTER_DIAMETER, WALL_DEPTH, DEPTH_PER_PASS)

# Bottom slot
clear_rect(Cncrect(-WALL_LENGTH/2, -WALL_LENGTH/2- BACK_OFFSET, WALL_LENGTH, WALL_THICKNESS), CUTTER_DIAMETER, WALL_DEPTH, DEPTH_PER_PASS)

# Touch sensor recess - only in the top.
clear_rect(Cncrect(-TOUCH_SENSOR_SIZE/2, -TOUCH_SENSOR_SIZE/2 - BACK_OFFSET, TOUCH_SENSOR_SIZE, TOUCH_SENSOR_SIZE), CUTTER_DIAMETER, WALL_DEPTH, DEPTH_PER_PASS)

 
cut_arc(CUTOUT_WIDTH,  Cncpoint(0, -INNER_RADIUS), Cncpoint(CENTER_X, CENTER_Y), CUTTER_DIAMETER, STOCK_THICKNESS - 1, DEPTH_PER_PASS)

emit_postamble()