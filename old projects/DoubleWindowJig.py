#!/usr/bin/env python3

from classes.rectangles import clear_rect, Cncrect, cut_outline_with_tabs
from classes.arcs import cut_arc, Cncpoint
from classes.ambles import emit_preamble, emit_postamble

# *****************************************************************************************
# Specific to THIS JIG.
# If you set these two values, there's no need to change anything else unless you also change something about the router bit or bushing or the stock size.
#
# This makes a jig that's useful for a router setup with a 1/2" bit and a 3/4" OD bushing.
# It's always a two-window jig that leaves a ridge down the middle for the router to rest on.
# Smaller cuts won't need two windows.
ROUTER_CUT_X = 137
ROUTER_CUT_Y = 109
# *****************************************************************************************

# Tool Setup
STOCK_THICKNESS = 11.65
CUTTER_DIAMETER = 25.4 / 4    # it's a 1/4" bit
DEPTH_PER_PASS = 3
CUT_THROUGH_DEPTH = 1

# Project Config
TAB_WIDTH = 25.4/4
TAB_HEIGHT = 25.4/4
CUTTER_OVERHANG = 25.4/8        # The bushing on the router that this jig will use is 3/4" OD, while the bit is 1/2".  This leaves us with 1/8" overhang on each side of the bit. 
OVERCUT = 4                     # The amount to cut extra in the Y direction so that the edges of the tenon cheeks turn out straight, 

BODY_X_EXT = 250
BODY_Y_EXT = 250
BODY_Z = STOCK_THICKNESS + CUT_THROUGH_DEPTH

SLOT_X = 0
SLOT_Y = 56
SLOT_Z = STOCK_THICKNESS / 2
SLOT_X_EXT = BODY_X_EXT
SLOT_Y_EXT = STOCK_THICKNESS

WHOLEWINDOW_X_EXT = ROUTER_CUT_X + 2 * CUTTER_OVERHANG
WHOLEWINDOW_Y_EXT = ROUTER_CUT_Y + 2 * CUTTER_OVERHANG + 2 * OVERCUT
WHOLEWINDOW_X = (BODY_X_EXT - WHOLEWINDOW_X_EXT) / 2
WHOLEWINDOW_Y = SLOT_Y + SLOT_Y_EXT - CUTTER_OVERHANG - OVERCUT
WINDOWBRIDGE_X_EXT = 25.4/4     # Divide the window into 2 parts to support the router.  This is a 1/4" bridge between the two window parts.

WINDOWL_X = WHOLEWINDOW_X
WINDOWL_Y = WHOLEWINDOW_Y
WINDOWL_Z = STOCK_THICKNESS + CUT_THROUGH_DEPTH
WINDOWL_X_EXT = WHOLEWINDOW_X_EXT / 2 - WINDOWBRIDGE_X_EXT / 2 
WINDOWL_Y_EXT = WHOLEWINDOW_Y_EXT

WINDOWR_X = WHOLEWINDOW_X + WINDOWL_X_EXT + WINDOWBRIDGE_X_EXT
WINDOWR_Y = WHOLEWINDOW_Y
WINDOWR_Z = STOCK_THICKNESS + CUT_THROUGH_DEPTH
WINDOWR_X_EXT = WINDOWL_X_EXT
WINDOWR_Y_EXT = WINDOWL_Y_EXT



emit_preamble()


# Jig Clamping Guide Slot
clear_rect(Cncrect(SLOT_X, SLOT_Y, SLOT_X_EXT, SLOT_Y_EXT), 
                    CUTTER_DIAMETER, SLOT_Z, DEPTH_PER_PASS)

# Left window
clear_rect(Cncrect(WINDOWL_X, WINDOWL_Y, WINDOWL_X_EXT, WINDOWL_Y_EXT), 
                    CUTTER_DIAMETER, WINDOWL_Z, DEPTH_PER_PASS)

# Right window
clear_rect(Cncrect(WINDOWR_X, WINDOWR_Y, WINDOWR_X_EXT, WINDOWR_Y_EXT), 
                    CUTTER_DIAMETER, WINDOWR_Z, DEPTH_PER_PASS)

# Outline
cut_outline_with_tabs(Cncrect(0, 0, BODY_X_EXT, BODY_Y_EXT), BODY_Z, DEPTH_PER_PASS, CUTTER_DIAMETER, TAB_WIDTH, TAB_HEIGHT)

emit_postamble()
