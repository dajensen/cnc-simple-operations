# Need some kind of global configuration object for this project

def travel_to(newloc, safe_height):
    print("G01 Z{:.4f}".format(safe_height))
    print("G00 X{:.4f} Y{:.4f}".format(newloc.x, newloc.y))

def set_depth(newdepth):
    print("G01 Z{:.4f}".format(-newdepth))

def retract(safe_height, speed=3000):
    if safe_height < 0:
        safe_height = -1 * safe_height
    print("G01 Z{:.4f} F{:.4f}  ( retract to safe height )".format(safe_height, speed))
