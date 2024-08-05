from labscript import start, stop, add_time_marker, AnalogOut, DigitalOut
from labscript_devices.DummyPseudoclock.labscript_devices import DummyPseudoclock
from labscript_devices.DummyIntermediateDevice import DummyIntermediateDevice
from user_devices.RemoteControl.labscript_devices import RemoteControl, RemoteAnalogOut, RemoteAnalogMonitor

from labscript_devices.NI_DAQmx.labscript_devices import NI_PCIe_6363

# Use a virtual, or 'dummy', device for the psuedoclock
DummyPseudoclock(name='pseudoclock')

# An output of this DummyPseudoclock is its 'clockline' attribute, which we use
# to trigger children devices
DummyIntermediateDevice(name='intermediate_device', parent_device=pseudoclock.clockline)

# Remote Operation of Laser Raster GUI
RemoteControl(name='LaserRasterGUI', host="10.0.0.180", port=55535, mock=False) # add IP address and Port of the host software

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
