#!/usr/bin/env python3

import math

from classes.ambles import emit_preamble, emit_postamble


MIN_SPACING = 8
STOCK_X_EXTENT = 276
GRID_X_EXTENT = 100.0
STOCK_Y_EXTENT = 63.5
Y_MAX_EXTENT = 45.0

Z_SAFE = 25
Z_TRAVEL = 5
Z_THICKNESS = 5.6
Z_EXTRA_DEPTH = 0.4

DRILL_FEED_RATE = 200
MOVE_FEED_RATE = 8000

def drill_hole():
    zpos = -(Z_THICKNESS + Z_EXTRA_DEPTH)
    print("G01 Z{:.4f} S{:.4f}".format(zpos, DRILL_FEED_RATE))
    print("G01 Z{:.4f}".format(Z_TRAVEL))

def calc_grid_from_x_extent(extent, minspacing):
    num_gaps = math.floor(extent / minspacing)
    if(num_gaps % 2 ==1):
        num_gaps = num_gaps - 1
    num_rows = num_gaps + 1
    return num_rows, extent / num_gaps

def calc_y_extent(max_extent, step_size):
    num_gaps = math.floor(max_extent / step_size)
    if(num_gaps % 2 == 1):
        num_gaps = num_gaps - 1
    num_rows = num_gaps + 1
    return num_rows, num_gaps * step_size

def drill_row(x_pos, y_pos, step_size, num_cols):
    col = 0
    while col < num_cols:
        print("G01 X{:.4f} Y{:.4f} S{:.4f}".format(x_pos, y_pos, MOVE_FEED_RATE))
        drill_hole()
        col = col + 2
        x_pos = x_pos + 2 * step_size

def outline_rectangle(x_pos, y_pos, x_extent, y_extent):
    print("( Outline rectangle: x {} y {} width {} height {}".format(x_pos, y_pos, x_extent, y_extent))
    print("G00 Z{:.4f}".format(Z_TRAVEL))
    print("G00 X{:.4f} Y{:.4f}".format(x_pos, y_pos))
    print("G01 X{:.4f} Y{:.4f}".format(x_pos, y_pos + y_extent))
    print("G01 X{:.4f} Y{:.4f}".format(x_pos + x_extent, y_pos + y_extent))
    print("G01 X{:.4f} Y{:.4f}".format(x_pos + x_extent, y_pos))
    print("G01 X{:.4f} Y{:.4f}".format(x_pos, y_pos))
 

emit_preamble()

print("")
print("(Drill a set of evenly spaced holes to form a grid)")
print("G00 X0 Y0 Z{:.4f}".format(Z_SAFE))
print("")

num_columns, step_size = calc_grid_from_x_extent(GRID_X_EXTENT, MIN_SPACING)
num_rows, y_extent = calc_y_extent(Y_MAX_EXTENT, step_size)
y_pos = y_bound = STOCK_Y_EXTENT / 2 - y_extent / 2
x_extent = GRID_X_EXTENT
x_pos = x_bound = (STOCK_X_EXTENT - GRID_X_EXTENT) / 2

# print("Calculated step_size as: {:.4f}".format(step_size))
# print("Calculated rows {} and cols {}".format(num_rows, num_columns))

print("G00 X{:.4f} Y{:.4f} Z{:.4f}".format(x_pos, y_pos, Z_TRAVEL))
# outline_rectangle(0, 0, STOCK_X_EXTENT, STOCK_Y_EXTENT)
# outline_rectangle(x_pos, y_pos, x_extent, y_extent)

is_odd_row = False
col = 0
row = 0
while row < num_rows:
    if is_odd_row:
        x_pos = x_bound + step_size
        cols_to_drill = num_columns - 1
    else:
        x_pos = x_bound
        cols_to_drill = num_columns
    drill_row(x_pos, y_pos, step_size, cols_to_drill)
    is_odd_row = not is_odd_row
    row = row + 1
    y_pos = y_pos + step_size

drill_hole()
x_pos = 0
y_pos = 0
print("G00 X{:.4f} Y{:.4f} Z{:.4f}".format(x_pos, y_pos, Z_SAFE))

emit_postamble()
