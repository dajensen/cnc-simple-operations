#! /usr/bin/python

from xml.dom.minidom import parse

import math
import os
#import sys
import re
from svgpathtools import svg2paths2
try:
    from os import PathLike as FilePathLike
except ImportError:
    FilePathLike = str

from collections import namedtuple

from classes.line import comment
from classes.arcs import Cncpoint
from classes.ambles import emit_preamble, emit_postamble
from classes.travel import travel_to, set_depth, retract

FILENAME = 'jigdefs/Testfile.svg'
SAFE_HEIGHT = 25
CUT_HEIGHT = -3
CURVE_QUALITY = 50


# Here are some functions adapted from a Javascript implementation found here:
#   https://observablehq.com/@awhitty/approximating-bezier-curves-for-cnc
# The original source of the pseudocode is wikipedia.
def b3p0(t, p):
  k = 1 - t
  return k * k * k * p

def b3p1(t, p):
  k = 1 - t
  return 3 * k * k * t * p

def b3p2(t, p):
  k = 1 - t
  return 3 * k * t * t * p

def b3p3(t, p):
  return t * t * t * p

def b3(t, p0, p1, p2, p3):
  return b3p0(t, p0) + b3p1(t, p1) + b3p2(t, p2) + b3p3(t, p3)


# This is a data class (namedtuple) that aggregates the information we need about the svg in all of the rendering functions
SvgCtx = namedtuple('SvgCtx', ['min_x', 'min_y', 'width', 'height'])

# This is adapted from svgpathtools.svg2paths, so that getting the svg viewbox will work exactly the same way as svgpathtools does.
# It can handle a path or a string of svg contents.
def get_viewbox(svg_file_location):

    from_filepath = isinstance(svg_file_location, str) or isinstance(svg_file_location, FilePathLike)
    svg_file_location = os.path.abspath(svg_file_location) if from_filepath else svg_file_location

    doc = parse(svg_file_location)

    def dom2dict(element):
        """Converts DOM elements to dictionaries of attributes."""
        keys = list(element.attributes.keys())
        values = [val.value for val in list(element.attributes.values())]
        return dict(list(zip(keys, values)))

    # Use minidom to extract path strings from input SVG
    svg = [dom2dict(el) for el in doc.getElementsByTagName('svg')]
    viewbox_strings = [el['viewBox'] for el in svg]
    if len(viewbox_strings) != 1:
        raise ValueError("Unable to find a viewBox element. Unable to flip the Y axis to generate gcode.")
    viewbox_string = viewbox_strings[0]
    min_x, min_y, width, height = viewbox_string.split(' ')
    return int(min_x), int(min_y), int(width), int(height)


# Functions for emitting gcode
def move_to(x, y, z = None):
    if z == None:
        print("G01 X{:.6f} Y{:.6f}".format(x, y))
    else:
        print("G01 X{:.6f} Y{:.6f} Z{:.6f}".format(x, y, z))

def segtype(seg):
    s = str(seg.__class__)
    m = re.findall(r"'svgpathtools.path.(.*?)'", s)
    return m[0]

# These functions convert from SVG coordinate space to gcode coordinate space
# They assume the machine is set up so that 0,0 is the origin for the machine, and that you shouldn't cut in negative space on the x or y axis.
# So they take the SVG and shift it in case the origin of the SVG is not zero.
# Additionally, the y axis is inverted between SVG and Gcode, so we flip the Y axis.
def convert_x(svgctx, xval):
    return xval - svgctx.min_x

def convert_y(svgctx, yval):
    scaled_y = yval - svgctx.min_y
    total_y = svgctx.height
    return total_y - scaled_y

# These functions will move to the end point following the correct function for the segment type
# They assume that the current position is already at the start point.
# If you're calling them through convert_to_gcode(), then that function has already confirmed this is true.
def convert_line(svgctx, seg):
    x = convert_x(svgctx, seg.end.real)
    y = convert_y(svgctx, seg.end.imag)

    move_to(x, y, CUT_HEIGHT)

def convert_arc(svgctx, seg):
    pass

def convert_quadratic_bezier(svgctx, seg):
    # Inkscape doesn't create quadratic beziers, but it also doesn't destroy them.  I need to support them.
    # There's a little editor embedded on this page: https://www.sitepoint.com/html5-svg-quadratic-curves/
    pass

def convert_cubic_bezier(svgctx, seg):

    for idx in range(CURVE_QUALITY + 1):
        t = idx / CURVE_QUALITY
        tx = b3(t, seg.start.real, seg.control1.real, seg.control2.real, seg.end.real)
        ty = b3(t, seg.start.imag, seg.control1.imag, seg.control2.imag, seg.end.imag)
        x = convert_x(svgctx, tx)
        y = convert_y(svgctx, ty)
        move_to(x, y, CUT_HEIGHT)

def convert_segment(svgctx, seg):
    segment_type = segtype(seg)
#    comment(segment_type)
    if segment_type == 'Line':
        convert_line(svgctx, seg)
    elif segment_type == 'Arc':
        convert_arc(svgctx, seg)
    elif segment_type == 'QuadBezier':
        convert_quadratic_bezier(svgctx, seg)
    elif segment_type == "CubicBezier":
        convert_cubic_bezier(svgctx, seg)
    else:
        raise ValueError("Segment type is unknown: " + segtype)

def make_transformed_path(path, xform_str):
    # DAJ todo: handle different transforms.  This is an example. We'll call path.rotated(), path.translated(), path.scaled() and chain them as necessary.
    print("Transform: " + xform_str)
    return path.rotated(27)

def get_start_point(svgctx, seg):
    # it appears that all segments have "start" and "end" attributes
    x = convert_x(svgctx, seg.start.real)
    y = convert_y(svgctx, seg.start.imag)
    return [x,y]

def get_end_point(svgctx, seg):
    # it appears that all segments have "start" and "end" attributes
    x = convert_x(svgctx, seg.end.real)
    y = convert_y(svgctx, seg.end.imag)
    return [x,y]

def convert_to_gcode(svgctx, path):
    started = False
    prev_x = None
    prev_y = None
    for seg in path:
#        print(seg)
        startx, starty = get_start_point(svgctx, seg)
        if not started:
            travel_to(Cncpoint(startx, starty), SAFE_HEIGHT)
            move_to(startx, starty, CUT_HEIGHT)
            started = True
        else:
            if startx != prev_x or starty != prev_y:
                raise ValueError("This path has discontinuous segments.  Those are NOT supported yet")
        convert_segment(svgctx, seg)
        prev_x, prev_y = get_end_point(svgctx, seg)

    retract(SAFE_HEIGHT)
    comment('')

emit_preamble()

paths, attributes, svg_attributes = svg2paths2(FILENAME)
min_x, min_y, width, height = get_viewbox(FILENAME)
ctx = SvgCtx(min_x, min_y, width, height)
comment('SVG dimensions: ')
comment('    min_x: ' + str(ctx.min_x))
comment('    min_y: ' + str(ctx.min_y))
comment('    width: ' + str(ctx.width))
comment('    height: ' + str(ctx.height))
comment('')


pathdict = {}

for i in range(len(paths)):
    id = attributes[i]['id']
    if "transform" in attributes[i]:
        pathdict[id] = make_transformed_path(paths[i], attributes[i]["transform"])
    else:
        pathdict[id] = paths[i]

#    print("PATH:" + attributes[i]['id'])
#    print(attributes[i])

comment('')

pathid = "TheSquare"
comment(pathid)
convert_to_gcode(ctx, pathdict[pathid])

#pathid = "WeirdBezier"
#comment(pathid)
#convert_to_gcode(ctx, pathdict[pathid])

pathid = "RotatedChord"
comment(pathid)
convert_to_gcode(ctx, pathdict[pathid])

pathid = "AChord"
comment(pathid)
convert_to_gcode(ctx, pathdict[pathid])

emit_postamble()
