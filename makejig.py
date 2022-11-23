#! /usr/bin/python

import sys
import json
from classes.ambles import emit_preamble, emit_postamble
from classes.rectangles import Cncrect, clear_rect, cut_outline, cut_outline_with_tabs, clear_y_ramp, contour_y_ramp, roundover
from classes.arcs import Cncpoint, cut_circle, cut_arc
from classes.ovals import cut_oval, cut_oval_with_tabs
from classes.drill import peckdrill
from classes.line import line

class StockInfo:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class ToolInfo:

    def __init__(self, diameter):
        self.diameter = diameter

class JobInfo:

    def __init__(self, depth_per_pass, tab_width, tab_height):
        self.depth_per_pass = depth_per_pass
        self.tab_width = tab_width
        self.tab_height = tab_height

class CncCut:

    def __init__(self, cut):
        if "name" in cut:
            self.name = cut["name"]
        else:
            self.name = "(unnamed)"
        if "disabled" in cut:
            self.disabled = cut['disabled']
        else:
            self.disabled = False
        try:
            if not "x" in vars(self):
                self.x = cut['x']
            if not "y" in vars(self):
                self.y = cut['y']
            if not "z" in vars(self):
                self.z = cut['z']
            if not "depth" in vars(self):
                self.depth = cut['depth']
            if not "width" in vars(self):
                self.width = cut['width']
            if not "height" in vars(self):
                self.height = cut['height']
        except AttributeError:
            dump_attribute_exception(self.name)

        if not self.disabled:
            if "cuts" in cut:
                self.cuts = []
                for childcut in cut["cuts"]:
                    newcut = load_cut(childcut)
                    self.cuts.append(newcut)

    def exec(self, stock, tool, job):
        raise ValueError('Unknown type of CncCut for object named \"{0}\"'.format(self.name))

class CncRect(CncCut):

    def __init__(self, cut):
        super().__init__(cut)

    def exec(self, stock, tool, job):
        if not self.disabled:
            # print('CncRect exec {0}'.format(self.name))
            clear_rect(Cncrect(self.x, self.y, self.width, self.height), tool.diameter, self.depth, job.depth_per_pass)

class CncCircle(CncCut):

    def __init__(self, cut):
        try:
            self.x = cut['center_x']
            self.y = cut['center_y']
            self.diameter = cut['diameter']

            self.width = self.diameter
            self.height = self.diameter
        except AttributeError:
            dump_attribute_exception(self.name)
        super().__init__(cut)

    def exec(self, stock, tool, job):
        if not self.disabled:
            #print('CncCircle exec {0}'.format(self.name))
            cut_circle(Cncpoint(self.x, self.y), self.diameter, self.z, self.depth, job.depth_per_pass, tool.diameter)

class CncOutline(CncCut):

    def __init__(self, cut):
        super().__init__(cut)
        self.bridges = False
        if "bridges" in cut:
            self.bridges = cut["bridges"].lower() == "true"

    def exec(self, stock, tool, job):
        if not self.disabled:
            if self.bridges:
                cut_outline_with_tabs(Cncrect(self.x, self.y, self.width, self.height), self.depth, job.depth_per_pass, tool.diameter, job.tab_width, job.tab_height)
            else:
                cut_outline(Cncrect(self.x, self.y, self.width, self.height), self.depth, job.depth_per_pass, tool.diameter)

class CncOvalOutline(CncCut):

    def __init__(self, cut):
        super().__init__(cut)
        self.bridges = False
        if "bridges" in cut:
            self.bridges = cut["bridges"].lower() == "true"
        # rounded_axis is required.  If it's missing or invalid, an exception will be thrown
        rounded_axis = cut["rounded_axis"].lower()
        if rounded_axis == 'x' or rounded_axis == 'y':
            self.rounded_axis =  rounded_axis
        else:
            raise ValueError("Oval object \"{0}\" has invalid value for rounded_axis.  Must be \"x\" or \"y\".".format(self.name))

    def exec(self, stock, tool, job):
        if not self.disabled:
            if self.bridges:
                cut_oval_with_tabs(Cncrect(self.x, self.y, self.width, self.height), self.rounded_axis == 'x', self.depth, job.depth_per_pass, tool.diameter, job.tab_width, job.tab_height)
            else:
                cut_oval(Cncrect(self.x, self.y, self.width, self.height), self.rounded_axis == 'x', self.depth, job.depth_per_pass, tool.diameter)

class CncRampClearingY(CncCut):

    def __init__(self, cut):
        try:
            self.depth_step = cut['depth_step']
            self.bottom_y_min = cut['bottom_y_min']
            self.bottom_y_max = cut['bottom_y_max']
        except AttributeError:
            dump_attribute_exception(self.name)
        super().__init__(cut)

    def exec(self, stock, tool, job):
        if not self.disabled:
            # print('CncRect exec {0}'.format(self.name))
            clear_y_ramp(Cncrect(self.x, self.y, self.width, self.height), 
                        self.bottom_y_min, self.bottom_y_max, tool.diameter, self.z, self.depth, self.depth_step)

class CncRampContourY(CncCut):

    def __init__(self, cut):
        try:
            self.depth_step = cut['depth_step']
            self.bottom_y_min = cut['bottom_y_min']
            self.bottom_y_max = cut['bottom_y_max']
        except AttributeError:
            dump_attribute_exception(self.name)
        super().__init__(cut)

    def exec(self, stock, tool, job):
        if not self.disabled:
            # print('CncRect exec {0}'.format(self.name))
            contour_y_ramp(Cncrect(self.x, self.y, self.width, self.height), 
                        self.bottom_y_min, self.bottom_y_max, tool.diameter, self.z, self.depth, self.depth_step)

class CncRoundover(CncCut):

    def __init__(self, cut):
        try:
            self.radius = cut['radius']
        except AttributeError:
            dump_attribute_exception(self.name)
        super().__init__(cut)

    def exec(self, stock, tool, job):
        if not self.disabled:
            # print('CncRect exec {0}'.format(self.name))
            roundover(Cncrect(self.x, self.y, self.width, self.height), self.radius,
                        tool.diameter, self.z, self.depth)

class CncPeckDrill(CncCut):

    def __init__(self, cut):
        try:
            self.x = cut['center_x']
            self.y = cut['center_y']
            self.width = 0
            self.height = 0
            self.depth_per_pass = cut['depth_per_pass']
            self.retract_height = cut['retract_height']
            self.feedrate = cut['feedrate']
        except AttributeError:
            dump_attribute_exception(self.name)
        super().__init__(cut)

    def exec(self, stock, tool, job):
        if not self.disabled:
            # print('CncRect exec {0}'.format(self.name))
            peckdrill(Cncrect(self.x, self.y, self.width, self.height), 
                self.z, self.depth, self.depth_per_pass, self.retract_height,self.feedrate )

class CncLine(CncCut):

    def __init__(self, cut):
        try:
            self.name = cut['name']
            self.x1 = cut['x1']
            self.y1 = cut['y1']
            self.x2 = cut['x2']
            self.y2 = cut['y2']
            self.x = self.x1
            self.y = self.y1
            self.depth = cut['depth']
            self.width = abs(self.x2-self.x1)
            self.height = abs(self.y2-self.y1)
            self.depth_per_pass = cut['depth_per_pass']
        except AttributeError:
            dump_attribute_exception(self.name)
        super().__init__(cut)

    def exec(self, stock, tool, job):
        if not self.disabled:
#            print('CncLine exec {0}'.format(self.name))
            line(self.x1, self.y1, self.z, self.x2, self.y2, self.depth, self.depth_per_pass)

# Exception and error handling
def dump_exception():
    type, value, traceback = sys.exc_info()
    if type.__name__ == 'KeyError':
        dump_key_error_exception()

    print("Exception type: {0}".format(type.__name__))
    for valitem in value.args:
        print("    {0}".format(valitem))
    exit()

def dump_key_error_exception():
    type, value, traceback = sys.exc_info()
    print('Unable to read REQUIRED key "{0}"'.format(value.args[0]))
    exit()

def dump_attribute_exception(objname):
    type, value, traceback = sys.exc_info()
    print('Object "{0}" is missing attribute {1}'.format(objname, value.args[0]))
    exit()

def error_exit(reason):
    print('BOGUS error exit: {0}'.format(reason))
    exit()

def dump_key_error_exception():
    type, value, traceback = sys.exc_info()
    print('Unable to read REQUIRED key "{0}"'.format(value.args[0]))
    exit()

def error_exit(reason):
    print('BOGUS error exit: {0}'.format(reason))
    exit()

# Functions to load specific elements
def load_stock_info(stocknode):
    return StockInfo(stocknode["x"], stocknode["y"], stocknode["z"])

def load_tool_info(toolnode):
    return ToolInfo(toolnode["diameter"])

def load_job_info(jobnode):
    return JobInfo(jobnode["depth_per_pass"], jobnode["tab_width"], jobnode["tab_height"])

def load_cut(cutnode):

    selfname = "(unnamed)"
    if "name" in cutnode:
        selfname = cutnode["name"]

    rv = None    
    try:
        if(cutnode['type'] == 'rect'):
            rv = CncRect(cutnode)
        elif(cutnode['type'] == 'outline'):
            rv = CncOutline(cutnode)
        elif(cutnode['type'] == 'circle'):
            rv = CncCircle(cutnode)
        elif(cutnode['type'] == 'oval_outline'):
            rv = CncOvalOutline(cutnode)
        elif(cutnode['type'] == 'ramp_clearing_y'):
            rv = CncRampClearingY(cutnode)
        elif(cutnode['type'] == 'ramp_contour_y'):
            rv = CncRampContourY(cutnode)
        elif(cutnode['type'] == 'roundover'):
            rv = CncRoundover(cutnode)
        elif(cutnode['type'] == 'peckdrill'):
            rv = CncPeckDrill(cutnode)
        elif(cutnode['type'] == 'line'):
            rv = CncLine(cutnode)
        else:
            rv =CncCut(cutnode)
    except AttributeError:
        dump_attribute_exception(selfname)
    return rv


def get_cut_count(cuts, accumulator):
    for childcut in cuts:
        accumulator = accumulator + 1
        if "cuts" in vars(childcut):
            num_children = 0
            num_children = get_cut_count(childcut.cuts, num_children)
            accumulator = accumulator + num_children
    return accumulator

def exec_all_cuts(cuts, stock, tool, job):
    for childcut in cuts:
        if "cuts" in vars(childcut):
            exec_all_cuts(childcut.cuts, stock, tool, job)
        childcut.exec(stock, tool, job)



# MAIN starts here
if len(sys.argv) < 2:
    error_exit("Path to the jig definition file must be the first parameter.  There are no other parameters available.")

filename = sys.argv[1]

try:
    jigdef_file = open(filename, 'r')
except:
    print("BOGUS: Unable to open {0}.  System error follows.".format(filename))
    dump_exception()

try:
    jigdef = json.load(jigdef_file)
except:
    print("BOGUS json parsing error")
    dump_exception()

try:
    stock = load_stock_info(jigdef['stock'])
    tool = load_tool_info(jigdef['tool'])
    job = load_job_info(jigdef['job'])
except:
    print('BOGUS exception loading a REQUIRED json element')
    dump_exception()

try:
    cuts = []
    if "cuts" in jigdef:
        for cut in jigdef["cuts"]:
            newcut = load_cut(cut)
            if newcut:
                cuts.append(newcut)
            else:
                error_exit("Unable to load cut")
    else:
        error_exit("This definition has no cuts to perform")
except:
    print("BOGUS exception loading a cut element")
    dump_exception()

print("( Stock dimensions: {0}, {1}, {2} )".format(stock.x, stock.y, stock.z))
print("( Tool diameter: {0} )".format(tool.diameter))
print("( Job depth per pass: {0} )".format(job.depth_per_pass))
print("( Total cuts: {0} )".format(get_cut_count(cuts, 0)))
print("( Executing all )")

emit_preamble()
exec_all_cuts(cuts, stock, tool, job)
emit_postamble()
