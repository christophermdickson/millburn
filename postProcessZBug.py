# postProcessZbug.py -- post process gcodee files to work around (presumed) Z-axis bug in grblhal/teensy 4.1 
#                       configured as a (5-axis) mill with active-low enable + step/direction signals.
#
# There appears to be a bug in either grblhal core or the iMXRT1062 driver that causes the Z-axis (only!) to move in the wrong direction 
# under certain conditions. This script is a workaround for that bug.
#  Viz. If:
#     1.  A G0 or G1 command, or a z-axis jog  is issued to move the Z-axis to a new position
#     2.  A subsequent G0 or G1 command, or z-axis jog is issued to move the Z-axis to a new position in the 
#         opposite direction to the first move.
#       Then:
#     3.  The second Z-axis move will intially be in the same direction as the first move, rather than in the opposite direction.
#     4.  If the second move is long enough (unknown how long is long enough), then after some (not yet determined) distance/time 
#         the Z-axis move will abruptly reverse direction and move in the correct direction for the remainder of the move. 
#     Notes:
#       -   The distance/time at which the Z-axis move reverses direction is apparently not consistent, and may vary from one instance 
#           to the next.
#       -   It is not known whether the bug is specific to the configuration of the grblhal controller, which in the case of the author is 
#           a grblhal-controlled mill with a 5-axis configuration, and all stepper drivers configured with active-low enable 
#           + step/direction signals.
#       -   Unsuccesful attempts to resolve the bug have included:
#           - clearing the (emulated) EEPROM/flash memory settings  of the  controller and reconfiguring it from scratch. 
#           - upgrading to the latest grblhal firmware build.
#           - physically swapping the outgoing y and z-axis stepper control signals. This resulted in the problem moving to the physical y-axis 
#             (thereby confirming that the problem is related to either the grblhal configuration, the grblhal code itself, or possibly some hidden 
#             value in the persistent (EEPROM/flash) configuration that is not exposed to the user.) 
#          -  changing the Z-axis stepper driver direction signal from active-low to active-high (even though it is known to be active-low)
#             ... this results in the Z-axis moving in the wrong direction for all moves, rather than just the second move in the sequence. (???)
#          -  experimenting with external pull-up resistors on the Z-axis direction signal.
#          -  experimenting with different Z-axis acceleration and velocity settings, as well as with the delay time and idle-power-off-time settings 
#          -  delaying the second move several seconds after completing the first move.

#       - One tactic that has been successful in avoiding the bug is to insert BOTH:

#           i)  an extra Z-axis move of 0.01mm in the desired direction, 
#         followed by: 
#           ii) a 5 second delay (G4 P5.0)

#         prior to the each direction changing Z-azis move. This seems to work in all cases, at the penalty of introducing a +/-0.01mm 
#         positioning error.  The error is cumulative, but in the case (e.g. ) a 2.5d pcb millling program the +/- direction errors will
#         effectively cancel out with the net result that the actual Z-axis milling height is out by only 0.01mm.

#       - speculation: the bug may be related to an assumption in the grblhal code that the Z-azis direction signal is active-high, 
#         and / or that it need only be toggled to change direction. If the signal is active-low, then the signal must be toggled twice to change direction.?
#
#  Regardless, The script below implements a successful workaround. Quite _why_ it works is so far a mystery, to the author, at least.


# Read the input gcode file and insert a 0.01mm Z-axis move (in the anticipated direction), followed by a five second delay,
# immediately prior to each direction-switching G0 or G1 z-azis move. The assumption is that that even though this will actually 
# move the Z-axis in the wrong direction:

#    - it will be a very short move, and the subsequent move will be in the correct direction.
#    - z-azis moves almost always occur in the opposite direction to the previous move, so the inserted moves 
#      should cancel out in the long run. If they don't cancel out, the error will be relatively small compared 
#      to a indeterminate-length move in the wrong direction, which is what the bug causes if not corrected.
#  
# usage: python postProcessZBug.py <inputfile> <outputfile

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

with open(inputfile, "r") as infil:
    lines = infil.readlines()   

# open the output file

Z_correction = 0.01   # this is the amount to move the Z-axis to correct for the bug in grblhal.
                          # initially set to 0.01mm. The absolute value of this setting will be applied in the direction
                          # of each Z-axis move command in the input file.
                          #                         
cumulative_Z_error = 0.00  # this is the cumulative error in the Z-axis position, which is the sum of the actual values
                           #  of the inserted Z-axis moves. This is for informational purposes only, and is not used in the
                           # calculations.    
initial_z = 0.0            # this is the (assumed) initial Z-axis position
current_z = 0.0            # this is the current Z-axis position
firstmove = True           # this is a flag to indicate that the first Z-axis move has been encountered 
z_dir_change = False       # this is a flag to indicate that the Z-axis direction has changed since the last move
move_count = 0             # this is a count of the total number of Z-axis moves in the input file
current_z_dir = 0          # this is the current direction of the Z-axis move (1 = up, -1 = down)

with open(outputfile, "w") as f:

    # loop through the lines in the input file, making the necessary changes and printing each line to the output file:

    #          - insert an additional z-axis move immediately prior to each direction-changing z-axis move
    #            (distance = 0.01mm, direction = same as the existing direction-switching move)

    for line in lines:
        # check if the line is a Z-axis move command 

        if line.startswith("G0") or line.startswith("G1") or line.startswith("G00") or line.startswith("G01"):
          # does the line contain a Z-axis move command?
          if 'Z' in line:
            #match = re.search(r'Z(-?\d+\.\d+)', line)
            match = re.search(r'Z(-?\d+)', line)
            if match:
                # extract the Z-axis coordinate, allowing for the fact that there may be  needed characters after it in the line
                # (i.e. the match may not be at the end of the line)

                # e.g. 'G1 Z10 F1000' or 'G0 Z-5.5'
                z = float(match.group(1))
                

                # is this the first Z-axis move?

                if firstmove:
                    if z > 0:
                        current_z_dir = 1
                    else:
                        current_z_dir = -1

                    current_z = z
                    move_count = 0
                    firstmove = False
                    print('INFO - initial Z-axis position is: ' + str(initial_z) +  ' first move is to Z = ' + str(z))
                else:
                    # has the Z-axis direction changed since the last move?
                    if (z - current_z) * current_z_dir < 0:
                        z_dir_change = True
                        current_z_dir = -current_z_dir
                        if z > current_z:
                            Z_correction = 0.01
                        else:
                            Z_correction = -0.01
                        shortMove_z = current_z + Z_correction
                        current_z = z  
                    else:
                        z_dir_change = False
                        current_z = z
                        Z_correction = 0.00
                    # insert the additional z-axis move immediately prior to the existing move 
                    # (make it a very slow move G1 move to give the controller time to process it without ambiguity do to possible competing interrupts)
                    #    question: how long does it take to move 0.01mm at 10mm/min?
                    #    answer: 0.01mm / 10mm/min = 0.001 minutes = 0.06 seconds
                    #            0.01mm / 0.0025mm/step = 4 steps
                    #            alternatively, 0.1mm / 0.0025mm/step = 40 steps
                    #                           40 steps at 10mm/min = 0.6 seconds
                    if z_dir_change:
                        f.write("G1 Z{:.2f} F10 \n".format(shortMove_z))
                        cumulative_Z_error += Z_correction
                        move_count += 1
                        # add 5 second delay
                        f.write("G4 P5.0\n")
                        print("INFO - inserted Z-axis move to correct for direction change: " + line)
                    else:
                        print("INFO - Z-axis move with no direction change: " + line)
            else:
                print("z = " + str(z))
                print("ERROR - no Z coordinate specified for Z-axis move: " + line)
                exit(1)
          else:
            print("INFO - non-Z-axis G0/1 move command: " + line)

        # now output the original line
        f.write(line)

    print('INFO - final Z-axis position is: ' + str(current_z) + '  cumulative Z-axis error is: ' + str(cumulative_Z_error)  + ' total Z-axis move count is: ' + str(move_count))
    print('INFO - output file ' + outputfile + ' has been created')