
def emit_preamble():
    print("""
( simple_operations by dave jensen )
( Software-independent Gcode )

G94 ( Millimeters per minute feed rate. )
G21 ( Units == Millimeters. )
G90 ( Absolute coordinates. )
G00 S24000 ( RPM spindle speed. )
G01 F3000.00000 ( Feed rate )

(Spindle on, clockwise)
M03
G00 X0 Y0 Z25 ( home and at safe height)

""")


def emit_postamble():
    print("""
G00 Z25.000000 ( retract )
G00 X0 Y0      ( return home )

M02 ( Program end. )
""")
