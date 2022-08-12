#!/usr/bin/env python3

from classes.rectangles import Cncrect, outline_rect, cut_outline_with_tabs
from classes.point import Cncpoint
from classes.line import cut_polyline
from classes.travel import travel_to, retract
from classes.ambles import emit_preamble, emit_postamble

# Tool Setup
CUTTER_DIAMETER = 0.5    # it's a 1/2 mm bit
DEPTH_PER_PASS = CUTTER_DIAMETER
SAFE_HEIGHT = 5

# Project Config
STOCK_X = 12
STOCK_Y = 8
STOCK_Z = 1.4
PIN_LENGTH = 3
INNER_RADIUS = 130 / 2
BIG_HEADER_SPACING = 2.54
SMALL_HEADER_SPACING = BIG_HEADER_SPACING / 2
MIDPOINT_X = STOCK_X / 2
BRIDGE_WIDTH = 1
BRIDGE_HEIGHT = 0.5


POLYLINES = (
    (Cncpoint(MIDPOINT_X, 0), Cncpoint(MIDPOINT_X, STOCK_Y)),
    (Cncpoint(MIDPOINT_X - SMALL_HEADER_SPACING, 0), Cncpoint(MIDPOINT_X - SMALL_HEADER_SPACING, PIN_LENGTH), Cncpoint(MIDPOINT_X - BIG_HEADER_SPACING, STOCK_Y - PIN_LENGTH), Cncpoint(MIDPOINT_X - BIG_HEADER_SPACING, STOCK_Y)),
    (Cncpoint(MIDPOINT_X + SMALL_HEADER_SPACING, 0), Cncpoint(MIDPOINT_X + SMALL_HEADER_SPACING, PIN_LENGTH), Cncpoint(MIDPOINT_X + BIG_HEADER_SPACING, STOCK_Y - PIN_LENGTH), Cncpoint(MIDPOINT_X + BIG_HEADER_SPACING, STOCK_Y)),
    (Cncpoint(MIDPOINT_X - 2 * SMALL_HEADER_SPACING, 0), Cncpoint(MIDPOINT_X - 2 * SMALL_HEADER_SPACING, PIN_LENGTH), Cncpoint(MIDPOINT_X - 2 * BIG_HEADER_SPACING, STOCK_Y - PIN_LENGTH), Cncpoint(MIDPOINT_X - 2 * BIG_HEADER_SPACING, STOCK_Y)),
    (Cncpoint(MIDPOINT_X + 2 * SMALL_HEADER_SPACING, 0), Cncpoint(MIDPOINT_X + 2 * SMALL_HEADER_SPACING, PIN_LENGTH), Cncpoint(MIDPOINT_X + 2 * BIG_HEADER_SPACING, STOCK_Y - PIN_LENGTH), Cncpoint(MIDPOINT_X + 2 * BIG_HEADER_SPACING, STOCK_Y))
)

emit_preamble()

for line in POLYLINES:
    travel_to(line[0], SAFE_HEIGHT)
    cut_polyline(line, DEPTH_PER_PASS)

travel_to(Cncpoint(0, 0), SAFE_HEIGHT)
outline_rect(Cncrect(0, 0, STOCK_X, STOCK_Y), DEPTH_PER_PASS)
cut_outline_with_tabs(Cncrect(0, 0, STOCK_X, STOCK_Y), STOCK_Z, DEPTH_PER_PASS, CUTTER_DIAMETER, BRIDGE_WIDTH, BRIDGE_HEIGHT)

emit_postamble()
