#!/usr/bin/env python3

from classes.ambles import emit_preamble, emit_postamble
from classes.rectangles import clear_rect, Cncrect

STEP_SIZE = 3
CUTTER_DIAMETER = 19.05
X_EXTENT = 520.0
Y_EXTENT = 520.0
Z_EXTENT = 3

# prev_x = 0.0
# xpos = 0.0
# ypos = 0.0

# print("")
# print("(Plane the surface with closely spaced horizontal passes)")
# print("G00 X0 Y0")
# print("")
# ypos = 0.0
# xpos = 0.0
# while(ypos < Y_EXTENT):
#     xpos = X_EXTENT - STEP_SIZE if xpos <= STEP_SIZE else STEP_SIZE
#     print("G01 X{:.4f} Y{:.4f}".format(xpos, ypos))
#     if ypos + STEP_SIZE < Y_EXTENT:
#         op = "G02" if xpos <= STEP_SIZE else "G03"
#         print("{} X{} Y{} R1.5000".format(op, xpos, ypos + STEP_SIZE))
#     ypos += STEP_SIZE

emit_preamble()
clear_rect(Cncrect(0, 0, X_EXTENT, Y_EXTENT), CUTTER_DIAMETER, Z_EXTENT, Z_EXTENT)

emit_postamble()
