from labscript import *
from labscript_devices.PulseBlasterUSB import PulseBlasterUSB
from labscript_devices.PineBlaster import PineBlaster
from labscript_devices.NI_DAQmx.labscript_devices import NI_PCIe_6363
from labscript_devices.FunctionRunner.labscript_devices import FunctionRunner

'''
Initialize the PulseBlaster as the Pseudoclock
and all the channels to be used
'''
# PulseBlasterUSB(name='pb',board_number=0,programming_scheme='pb_start/BRANCH')
# ClockLine(name='pb_clock_line', pseudoclock=pb.pseudoclock,connection='flag 0')
PineBlaster(name='pb', usbport='COM3')
'''
Initialize the NI Hardware and all the channels
to be used on each card
'''
ni_6363_max_name = "ni_6363"

NI_PCIe_6363(
    name='ni_6363', 
    parent_device=pb_clock_line,
    clock_terminal=f'/{ni_6363_max_name}/PFI1',
    MAX_name=f'{ni_6363_max_name}',
    acquisition_rate=1000e3,
    stop_order=-1,
)

# Analog Output Channels
AnalogOut(name='ao0', parent_device=ni_6363, connection='ao0')
AnalogOut(name='ao1', parent_device=ni_6363, connection='ao1')

# Digital Output Channels
DigitalOut(
    name='do0', parent_device=ni_6363, connection='port0/line0'
)
DigitalOut(
    name='do1', parent_device=ni_6363, connection='port0/line1'
)

# Analog Input Channels
AnalogIn(name="ai0", parent_device=ni_6363, connection='ai0')
AnalogIn(name="ai1", parent_device=ni_6363, connection='ai1')
AnalogIn(name="ai2", parent_device=ni_6363, connection='ai2')
AnalogIn(name="ai3", parent_device=ni_6363, connection='ai3')

if __name__ == '__main__':
    # Begin issuing labscript primitives
    # start() elicits the commencement of the shot
    start()

    # Stop the experiment shot with stop()
    stop(1.0)
