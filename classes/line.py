from .point import Cncpoint
from classes.travel import travel_to, set_depth, retract

SAFE_HEIGHT = 25


def comment(str = None):
    if str:
        print("( {} )".format(str))
    else:
        print("")

def cut_polyline(points, depth):
    # uses Cncpoint as points
    print("( Cutting polyline )")
    for i in range(len(points)):
        print("G01 X{:.4f} Y{:.4f}".format(points[i].x, points[i].y))
        if i == 0:
            print("G01 Z{:.4f}".format(-depth))

    print("( End polyline )")

def cut_polyline3d(points, depth):
    # Uses Cncpoint3d as points
    print("( Cutting polyline3d )")
    for i in range(len(points)):
        if i == 0:
            print("G01 X{:.4f} Y{:.4f}".format(points[i].x, points[i].y))
        print("G01 X{:.4f} Y{:.4f} Z{:.4f}".format(points[i].x, points[i].y, points[i].z))

    print("( End polyline )")

def cut_rotary_line(point):
    # Uses Cncpoint4d as point
    print("G01 X{:.4f} Z{:.4f} A{:.4f}".format(point.x, point.z, point.a))

def draw_line_on_plane(x, y):
    print("G01 X{:.4f} Y{:.4f}".format(x, y))

def line(x1, y1, z, x2, y2, depth, depth_per_pass):
    comment()
    comment("Cut line")
    zpos = z
    while zpos < z + depth:
        zpos = min(zpos + depth_per_pass, z + depth)
        travel_to(Cncpoint(x1, y1), SAFE_HEIGHT)
        set_depth(zpos)
        draw_line_on_plane(x2, y2)

    retract(SAFE_HEIGHT)
