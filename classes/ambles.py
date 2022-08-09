
def emit_preamble():
    print("""
( simple_operations by dave jensen )
( Software-independent Gcode )

G94 ( Millimeters per minute feed rate. )
G21 ( Units == Millimeters. )
G90 ( Absolute coordinates. )
G00 S24000 ( RPM spindle speed. )
G01 F3000.00000 ( A high feed rate, NOT SUITABLE for circuit boards )

(Spindle on, clockwise)
M03

""")


def emit_postamble():
    print("""
G00 Z25.000000 ( retract )

M02 ( Program end. )
""")
