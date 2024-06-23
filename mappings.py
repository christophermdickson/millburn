# mappings.py  # This file contains the rules for laser power > feed rate/cut depth/number-of-passes mapping

# Distance, Time and Rate units are dependant on the GCode file.  At present, the units are set to mm, seconds and mm/min respectively.

# NOTE: The GCode file should specify the units in the header.  If the units 
#       are different, the following variables should be changed accordingly.

#GodeHeader = 'G21\nG90\nG17\nG94\n' # Units: mm, seconds, mm/min
GodeHeader = 'G17\nG21\nG40\nG80\nG90\nG17\nG94\n' # Units: mm, seconds, mm/min
'''
G17 use XY plane,
G20 inch mode,
G40 cancel diameter compensation, 
G49 cancel length offset, G54 use coordinate system 1, 
G80 cancel canned cycles, 
G90 absolute distance mode, 
G94 feed/minute mode.
G17 G21 G40 G49 G54 G80 G90 G94
'''
# ZClearance: mm
# ZClearance is the height above the workpiece that the spindle will move to when not cutting.
# This is used to avoid the workpiece when moving between cutting locations.

# input laser cutting/engraving file values
LaserCuttingPowerMin=700
LaserCuttingPowerMax=1000
LaserEngravingPowerMin=100
LaserEngravingPowerMax=699

# output mill cutting/engraving file values
ZClearance = 3
MaterialThickness = 3
MaterialType = 'acrylic'
CutterMinSpeed = 2000
CutterMaxSpeed = 12000

#use fixed speed + feed rate for engraving
defaultSpindleSpeed = 5000
defaultFeedRate = 400
DepthPerPass = 0.1
NumberOfPasses = 2

# laser power: spindle speed ratio is not linear. Rather, the laser power value + feed rate specified by Snnn + Fnnn values in the input G1 code lines 
# are used to determine whether this is an engraving or cutting operation. 
# The SMapping lookup table is used to map the laser power to the spindle speed.