from labscript import *
from labscript_devices.PulseBlasterUSB import PulseBlasterUSB
from labscript_devices.DummyIntermediateDevice import DummyIntermediateDevice

# Use a virtual, or 'dummy', device for the psuedoclock
PulseBlasterUSB(name='pb',board_number=0,programming_scheme='pb_start/BRANCH')
ClockLine(name='pb_clockline_fast', pseudoclock=pb.pseudoclock,connection='flag 0')

# An output of this DummyPseudoclock is its 'clockline' attribute, which we use
# to trigger children devices
# DummyIntermediateDevice(name='intermediate_device', parent_device=pseudoclock.clockline)

# Create an AnalogOut child of the DummyIntermediateDevice
# AnalogOut(name='analog_out', parent_device=intermediate_device, connection='ao0')

# Create a DigitalOut child of the DummyIntermediateDevice
# DigitalOut(
#     name='digital_out', parent_device=intermediate_device, connection='port0/line0'
# )

# Begin issuing labscript primitives
# A timing variable t is used for convenience
# start() elicits the commencement of the shot
t = 0
# add_time_marker(t, "Start", verbose=True)
start()

# Wait for 1 second with all devices in their default state
t += 0.1

# Change the state of digital_out, and denote this using a time marker
# add_time_marker(t, "Toggle digital_out (high)", verbose=True)
# digital_out.go_high(t)

# Wait for 0.5 seconds
# t += 0.5

# Ramp analog_out from 0.0 V to 1.0 V over 0.25 s with a 1 kS/s sample rate
# t += analog_out.ramp(t=t, initial=0.0, final=1.0, duration=0.25, samplerate=1e3)

# Change the state of digital_out, and denote this using a time marker
# add_time_marker(t, "Toggle digital_out (low)", verbose=True)
# digital_out.go_low(t)

# Wait for 0.5 seconds
# t += 0.5

# Stop the experiment shot with stop()
stop(t)
