# millburn
Convert cutting/engraving gcode between laser + mill cutter

WARNING!!!

    Caution! -- Work-In-Progress -- this code is almost certainly broken.

    -- Use at your own risk!

    -- If you _must_ use it, expect it to fail horribly, with ensuing material and machine 
        destruction, injury and/or death.

    -- Better yet, don't!

YOU HAVE BEEN WARNED.

usage: python millburn.py <laserburn-gcode>.nc <2.5d_mill-engraving-gcode>.nc

Version History:
2024-06-19    v0.0.1   - Initial version. Happy-path-tested only with a simple, 2-layer lightburn-generated .nc file 

                           - inserts z-axis clearance G0 codes before+after each pre-existing G0 rapid move.
                             (clearance height is specified by parameter 'ZClearance' in mappings.py)
			   - replaces G1 Fxxx and Sxxx values with default spindle speed and feed rate for cutting.
			   - passes non G0/G1 lines through unchanged.

			TODOS:
                           - remap laser power:spindle speeds specified by Snnn values in G1 code lines according to the SMapping lookup table in 'mappings.py'
                           - remap feed rates specified by Fnnn values in G1 code lines according to the FMapping lookup table in 'mappings.py'
                           - switch grbl ???$35??? value from laser to spindle mode.
                           - deal with M* codes as appropriate


