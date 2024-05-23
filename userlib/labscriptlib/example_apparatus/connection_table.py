from labscript import *
from labscript_devices.PulseBlasterUSB import PulseBlasterUSB
from labscript_devices.DummyIntermediateDevice import DummyIntermediateDevice

# Use a virtual, or 'dummy', device for the psuedoclock
PulseBlasterUSB(name='pb',board_number=0,programming_scheme='pb_start/BRANCH')
ClockLine(name='pb_clockline_fast', pseudoclock=pb.pseudoclock,connection='flag 0')

# An output of this DummyPseudoclock is its 'clockline' attribute, which we use
# to trigger children devices
DummyIntermediateDevice(name='intermediate_device', parent_device=pb_clockline_fast)

# Create an AnalogOut child of the DummyIntermediateDevice
AnalogOut(name='analog_out', parent_device=intermediate_device, connection='ao0')

# Create a DigitalOut child of the DummyIntermediateDevice
DigitalOut(
    name='digital_out', parent_device=intermediate_device, connection='port0/line0'
)

if __name__ == '__main__':
    # Begin issuing labscript primitives
    # start() elicits the commencement of the shot
    start()

    # Stop the experiment shot with stop()
    stop(1.0)
