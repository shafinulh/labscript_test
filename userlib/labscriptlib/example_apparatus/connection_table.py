from labscript import *
from labscript_devices.PulseBlasterUSB import PulseBlasterUSB
from labscript_devices.PineBlaster import PineBlaster
from labscript_devices.PrawnBlaster.labscript_devices import PrawnBlaster
from labscript_devices.NI_DAQmx.labscript_devices import NI_PCIe_6363, NI_PXIe_6535, NI_PXIe_6361, NI_PXIe_6739
from labscript_devices.FunctionRunner.labscript_devices import FunctionRunner
from user_devices.RemoteControl.labscript_devices import RemoteControl, RemoteAnalogOut, RemoteAnalogMonitor

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

# Remote Operation of Laser Raster GUI 
# RemoteControl(name='LaserRasterGUI', ip_address="10.0.0.180", port=55535, mock=False) # add IP address and Port of the host software 
RemoteControl(name='LaserRasterGUI', mock=True) # add IP address and Port of the host software 

RemoteAnalogOut( 
    name='Laser_X_Control',  
    parent_device=LaserRasterGUI,  
    connection='laser_raster_x_coord', 
    units="mm", 
    decimals=3 
) 
RemoteAnalogOut( 
    name='Laser_Y_Control',  
    parent_device=LaserRasterGUI,  
    connection='laser_raster_y_coord', 
    units="mm", 
    decimals=3 
) 
RemoteAnalogMonitor( 
    name='Laser_X_Monitor',  
    parent_device=LaserRasterGUI,  
    connection='laser_raster_x_coord_monitor', 
    units="mm", 
    decimals=3 
) 
RemoteAnalogMonitor( 
    name='Laser_Y_Monitor',  
    parent_device=LaserRasterGUI,  
    connection='laser_raster_y_coord_monitor', 
    units="mm", 
    decimals=3 
) 

if __name__ == '__main__':
    # Begin issuing labscript primitives
    # start() elicits the commencement of the shot
    start()

    # Stop the experiment shot with stop()
    stop(1.0)
