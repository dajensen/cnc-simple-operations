from .point import Cncpoint

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
