# millburn.py -- convert a lightburn -compatible .nc file into a form that 
# can be used to generate a toolpath for a mill.  This is a simple script that reads the gcode file
# and converts the laser commands into mill commands.  It is not perfect, but it is a start.
# 
# if you have a gcode file that you want to convert, you can run this script as follows:
# python millburn.py <inputfile> <outputfile>
# 

import sys
import re
from mappings import *

if len(sys.argv) != 3:
    print("Usage: python millburn.py <inputfile> <outputfile>")
    sys.exit(1)

inputfile = sys.argv[1]
outputfile = sys.argv[2]
OutputPower = 0
OutputFeedRate = 0.0
CurrentZ = 0.0


with open(inputfile, "r") as f:
    lines = f.readlines()   

# open the output file

with open(outputfile, "w") as f:

    # write the header
    # f.write("G21\n")
    # f.write("G90\n")
    # f.write("G17\n")
    # f.write("G94\n")

    # loop through the lines in the input file, making the necessary changes and printing each line to the output file
    # The following is a description of the changes that are made:

    #          - inserts z-axis clearance G0 codes before+after each pre-existing G0 rapid move.
    #            (clearance height is specified by parameter 'ZClearance' in mappings.py)
    #          - remaps laser power:spindle speeds specified by Snnn values in G1 code lines according to the SMapping lookup table in 'mappings.py'
    #          - remaps feed rates specified by Fnnn values in G1 code lines according to the FMapping lookup table in 'mappings.py'
    #          - switches grbl ???$35??? value from laser to spindle mode.
    #          - deals with M* codes as appropriate

    for line in lines:
        # check if the line is a laser command
        #print('processing: ' + line)
        if line.startswith("G1"):
            # extract the x and y coordinates
            match = re.search(r'X(-?\d+\.\d+)', line)
            if match:
                x = float(match.group(1))
                XwasSpecified = True
            else:
                XwasSpecified = False

            match = re.search(r'Y(-?\d+\.\d+)', line)
            if match:
                y = float(match.group(1))
                YwasSpecified = True
            else:
                YwasSpecified = False

            match = re.search(r'Z(-?\d+\.\d+)', line)
            if match:
                z = float(match.group(1))
                ZwasSpecified = True
            else:
                ZwasSpecified = False

            # extract the laser power
            match = re.search(r'S(\d+\.\d+)', line)
            if match:
                inputPower = int(match.group(1))
                powerWasSpecified = True
            else:
                powerWasSpecified = False

            #extract the feed rate
            match = re.search(r'F(\d+\.\d+)', line)
            if match:
                inputFeedRate = float(match.group(1))
                feedRateWasSpecified = True
            else:
                feedRateWasSpecified = False

            # if the power and feedrate are known to be greater than 0, 
            # or write a move command,
            # otherwise write a sequence of rapid move commands to move up to the clearance height,
            # then move to the x and y coordinates, and then move back down to the cutting height.
            if feedRateWasSpecified:
                #OutputFeedRate = defaultFeedRate
                OutputFeedRate = inputFeedRate  
                print('INFO - feed rate was specified as: ' + str(OutputFeedRate))
            if powerWasSpecified:
                OutputPower = defaultSpindleSpeed
                #OutputPower = inputPower
        
            if XwasSpecified and YwasSpecified and not ZwasSpecified:
                if powerWasSpecified and feedRateWasSpecified:
                    f.write("G1 X{:.2f} Y{:.2f} S{:.2f} F{:.2f}\n".format(x, y, OutputPower, OutputFeedRate))
                    print("G1 X{:.2f} Y{:.2f} S{:.2f} F{:.2f}".format(x, y, OutputPower, OutputFeedRate))
                elif powerWasSpecified:
                    f.write("G1 X{:.2f} Y{:.2f} S{:.2f}\n".format(x, y, OutputPower))
                    print("G1 X{:.2f} Y{:.2f} S{:.2f}".format(x, y, OutputPower))
                elif feedRateWasSpecified:
                    f.write("G1 X{:.2f} Y{:.2f} F{:.2f}\n".format(x, y, OutputFeedRate))
                    print("G1 X{:.2f} Y{:.2f} F{:.2f}".format(x, y, OutputFeedRate))
                else:
                    f.write(line)
                    #print(line)
                    continue
            elif XwasSpecified and not YwasSpecified and not ZwasSpecified:
                f.write(line)
                #print(line)
                continue
            elif not XwasSpecified and YwasSpecified and not ZwasSpecified:
                f.write(line)
                #print(line)
                continue
            elif ZwasSpecified:
                print('WARNING - Z was specified in G1 command. passing through unchanged\n \
                               - and setting CurrentZ to ' + str(z) + 'check if this is correct')
                CurrentZ = z
                f.write(line)
                continue
            '''
            if ZwasSpecified:

                if powerWasSpecified:
                    if inputPower != OutputPower:
                        OutputPower = inputPower
                        print('INFO - power change was specified')  

                    #OutputPower = defaultSpindleSpeed
                    #insert dwell time here to allow spindle to reach speed
                    f.write("G4 P2.0\n")

                    f.write("G1 X{:.2f} Y{:.2f} S{:.2f} F{:.2f}\n".format(x, y, OutputPower, OutputFeedRate))
                    print('WARNING - power was specified -- writing anyway as: G1 X{:.2f} Y{:.2f} S{:.2f} F{:.2f}'.format(x, y, OutputPower, OutputFeedRate))
                else:
                    f.write("G1 X{:.2f} Y{:.2f} F{:.2f}\n".format(x, y, OutputFeedRate))
                    print('INFO - feed rate was specified - writing as: G1 X{:.2f} Y{:.2f} F{:.2f}'.format(x, y, OutputFeedRate))

            else:
                if OutputPower != 0 and OutputFeedRate != 0:
                    f.write(line)
                    print('line')
                else:
                    print ('WARNING - no feed rate specified or in effect for G1 command, but outputting anyway')
                    f.write(line)
                    print('line: ' + line)
                #print("ERROR - no feed rate specified for G1 command")
                #exit(1)
            '''
        elif line.startswith("G00"):
            f.write(line)   #assume that this is the header line ( e.g. G00 G17 G21 G40 G49 G54 G80 G90 G94)
    
        elif line.startswith("G0"):
            f.write("G0 Z{:.2f}\n".format(ZClearance))
            f.write(line)
            f.write("G0 Z{:.2f}\n".format(CurrentZ))
            #f.write("G1 Z-{:.2f}\n".format(ZClearance))
            print(line)
            print('INFO - wrote G0 commands for moving to clearance height, then to X,Y coordinates, then back down to cutting height') 
        else:
            f.write(line)
            print('passing through: ' + line)

'''
            # extract the x and y coordinates
            match = re.search(r'X(-?\d+\.\d+)', line)
            if match:
                x = float(match.group(1))
                XwasSpecified = True
            else:
                XwasSpecified = False

            match = re.search(r'Y(-?\d+\.\d+)', line)
            if match:
                y = float(match.group(1))
                YwasSpecified = True
            else:
                YwasSpecified = False

            match = re.search(r'Z(-?\d+\.\d+)', line)
            if match:
                z = float(match.group(1))
                print('INFO - Z was specified as: ' + str(z))
                ZwasSpecified = True
            else:
                print('INFO - Z was not specified')
                ZwasSpecified = False

            if XwasSpecified == True and YwasSpecified == True and ZwasSpecified == False:
                f.write("G0 Z{:.2f}\n".format(ZClearance))
                f.write("G0 X{:.2f} Y{:.2f}\n".format(x, y))
                f.write("G1 Z-{:2f}\n".format(ZClearance))
                print('INFO - wrote G0 commands for moving to clearance height, then to X,Y coordinates, then back down to cutting height')
            else:
                print("ERROR - laserburn input G0 command should specify X and Y coordinates and not Z coordinates")
                print("ERROR - input line: " + line)
                print ('X,Y,ZwasSpecified: ' + str(XwasSpecified) + ',' + str(YwasSpecified) + ',' + str(ZwasSpecified))
                print("ERROR - don't know what to do with this... exiting")
                exit(1)
        elif line.startswith("M3"):
            # if the line is a laser on command, write a spindle on command
            f.write("M3\n")
        elif line.startswith("M5"):
            # if the line is a laser off command, write a spindle off command
            f.write("M5\n")
        elif line.startswith("M30"):
            # if the line is an end of program command, write the end of program command
            f.write("M30\n")
        else:
            # if the line is not a laser command, write the line as is
            print('passing through: ' + line)
            f.write(line)
'''
        # write the footer
        # f.write("M05\n")
        # f.write("M30\n")