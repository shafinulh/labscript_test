from labscript import *
from labscript_devices.PulseBlasterUSB import PulseBlasterUSB
from labscript_devices.NI_DAQmx.labscript_devices import NI_PCIe_6363

'''
Initialize the PulseBlaster as the Pseudoclock
and all the channels to be used
'''
PulseBlasterUSB(name='pb',board_number=0,programming_scheme='pb_start/BRANCH')
ClockLine(name='pb_clockline_fast', pseudoclock=pb.pseudoclock,connection='flag 0')

'''
Initialize the NI Hardware and all the channels
to be used on each card
'''
ni_6363_max_name = "ni_6363"

NI_PCIe_6363(
    name='ni_6363', 
    parent_device=pb_clockline_fast,
    clock_terminal=f'/{ni_6363_max_name}/PFI0',
    MAX_name=f'{ni_6363_max_name}',
    acquisition_rate=1e4,
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

if __name__ == '__main__':
    # Begin issuing labscript primitives
    # start() elicits the commencement of the shot
    start()

    # Stop the experiment shot with stop()
    stop(1.0)
