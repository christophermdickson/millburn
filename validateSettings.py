import serial


def send_command(ser, command):
    ser.write((command + '\n').encode())
    response = ser.readline().decode().strip()
    return response

def verify_settings(expected_settings):
    # Connect to the CNC machine
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    
    # Query current settings
    send_command(ser, "$$")
    response = ser.read(ser.in_waiting).decode().split('\n')
    
    # Parse current settings
    current_settings = {}
    for line in response:
        if line.startswith('$'):
            param, value = line.split('=')
            current_settings[param] = value
    
    # Verify settings
    for param, expected_value in expected_settings.items():
        if current_settings.get(param) != expected_value:
            print(f"Mismatch in {param}: expected {expected_value}, found {current_settings.get(param)}")
            return False
    
    return True

expected_settings = {
    "$100": "250.000",  # X steps/mm
    "$101": "250.000",  # Y steps/mm
    "$102": "250.000",  # Z steps/mm
    # Add more settings as needed
}

if verify_settings(expected_settings):
    print("Machine settings are correct.")
else:
    print("Machine settings are incorrect. Halting execution.")

def reset_G54_offsets_to_Zero():

    # Connect to the CNC machine
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    # reset all offests to zero
    send_command(ser, "G10 L2 P0 X0 Y0 Z0")
    # Reset G54, G55, G56 offsets to zero
    send_command(ser, "G10 L20 P0 X0 Y0 Z0")

    send_command(ser, "G10 L20 P1 X0 Y0 Z0")
    send_command(ser, "G10 L20 P2 X0 Y0 Z0")
    send_command(ser, "G10 L20 P3 X0 Y0 Z0")
    
    ser.close()


