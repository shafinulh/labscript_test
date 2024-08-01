from labscript import *
from labscript_devices.PulseBlasterUSB import PulseBlasterUSB
from labscript_devices.PineBlaster import PineBlaster
from labscript_devices.PrawnBlaster.labscript_devices import PrawnBlaster
from labscript_devices.NI_DAQmx.labscript_devices import NI_PCIe_6363, NI_PXIe_6535, NI_PXIe_6361, NI_PXIe_6739
from labscript_devices.FunctionRunner.labscript_devices import FunctionRunner

'''
Initialize the PulseBlaster as the Pseudoclock
and all the channels to be used
'''
# PulseBlasterUSB(name='pb',board_number=0,programming_scheme='pb_start/BRANCH')
# ClockLine(name='pb_clock_line', pseudoclock=pb.pseudoclock,connection='flag 0')
# PineBlaster(name='pb', usbport='COM3')
PrawnBlaster(name='pb',com_port='COM5')

'''
Initialize the NI Hardware and all the channels
to be used on each card
'''
ni_6363_max_name = "ni_6363"
NI_PCIe_6363(
    name='ni_6363_mio', 
    parent_device=pb_clock_line_0,
    clock_terminal=f'/{ni_6363_max_name}/PFI1',
    MAX_name=f'{ni_6363_max_name}',
    acquisition_rate=1000e3,
)
AnalogOut(name='ao0_6363', parent_device=ni_6363_mio, connection='ao0')
AnalogOut(name='ao1_6363', parent_device=ni_6363_mio, connection='ao1')
DigitalOut(name='do0_6363', parent_device=ni_6363_mio, connection='port0/line0')
DigitalOut(name='do1_6363', parent_device=ni_6363_mio, connection='port0/line1')
AnalogIn(name='ai0_6363', parent_device=ni_6363_mio, connection='ai0')
AnalogIn(name='ai1_6363', parent_device=ni_6363_mio, connection='ai1')


ni_6361_max_name = "PXI1Slot8"
NI_PXIe_6361(
    name='ni_6361_mio', 
    parent_device=pb_clock_line_0,
    clock_terminal=f'/{ni_6361_max_name}/PFI1',
    MAX_name=f'{ni_6361_max_name}',
    acquisition_rate=1000e3,
)
AnalogOut(name='ao0_6361', parent_device=ni_6361_mio, connection='ao0')
AnalogOut(name='ao1_6361', parent_device=ni_6361_mio, connection='ao1')
DigitalOut(name='do0_6361', parent_device=ni_6361_mio, connection='port0/line0')
DigitalOut(name='do1_6361', parent_device=ni_6361_mio, connection='port0/line1')
AnalogIn(name='ai0_6361', parent_device=ni_6361_mio, connection='ai0')
AnalogIn(name='ai1_6361', parent_device=ni_6361_mio, connection='ai1')


ni_6365_max_name = "PXI1Slot5"
NI_PXIe_6535(
    name='ni_6365_dio', 
    parent_device=pb_clock_line_0,
    clock_terminal=f'/{ni_6365_max_name}/PFI1',
    MAX_name=f'{ni_6365_max_name}',
)
DigitalOut(name='do0_6535', parent_device=ni_6365_dio, connection='port0/line0')
DigitalOut(name='do1_6535', parent_device=ni_6365_dio, connection='port0/line1')
DigitalOut(name='do2_6535', parent_device=ni_6365_dio, connection='port0/line2')
DigitalOut(name='do3_6535', parent_device=ni_6365_dio, connection='port0/line3')

ni_6739_max_name = "PXI1Slot3"
NI_PXIe_6739(
    name='ni_6739_ao', 
    parent_device=pb_clock_line_0,
    clock_terminal=f'/{ni_6739_max_name}/PFI1',
    MAX_name=f'{ni_6739_max_name}',
)
AnalogOut(name='ao0_6739', parent_device=ni_6739_ao, connection='ao0')
AnalogOut(name='ao1_6739', parent_device=ni_6739_ao, connection='ao4')
AnalogOut(name='ao2_6739', parent_device=ni_6739_ao, connection='ao8')
AnalogOut(name='ao3_6739', parent_device=ni_6739_ao, connection='ao12')


if __name__ == '__main__':
    # Begin issuing labscript primitives
    # start() elicits the commencement of the shot
    start()

    # Stop the experiment shot with stop()
    stop(1.0)
