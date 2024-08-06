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
    acquisition_rate=acq_rate,
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

'''
Define the Experiment Logic
'''

def digital_output_stream():
    t=0
    t+=0.01
    add_time_marker(t, "DO high", verbose=True)
    do0.go_high(t)
    t+=0.025
    add_time_marker(t, "DO low", verbose=True)
    do0.go_low(t)
    t+=0.02
    do0.go_high(t)
    t+=0.01
    do0.go_low(t)
    t += 0.05
    return t
def analog_output_stream():
    t=0.035
    add_time_marker(t, "Sending Analog Ramp", verbose=True)
    ao0.ramp(t=t, initial=0.0, final=1.0, duration=0.025, samplerate=1e4)
    t+=0.025
    ao0.constant(t=t, value=0)
    return t
def analog_input_stream():
    t=0.06
    ai0.acquire(label='measurement1', start_time=t, end_time=t+0.01)
    return t
t=0
start()
t=max(t, digital_output_stream())
t=max(t, analog_output_stream())
t=max(t, analog_input_stream())
print(t)
stop(t)


# t=0
# start()
# t+=0.01
# add_time_marker(t, "DO high", verbose=True)
# do0.go_high(t)
# t+=0.025
# add_time_marker(t, "Sending Analog Ramp", verbose=True)
# ao0.ramp(t=t, initial=0.0, final=1.0, duration=0.025, samplerate=1e3)
# end_val = t + 0.025
# ao0.constant(t=end_val, value=0)
# add_time_marker(t, "DO low", verbose=True)
# do0.go_low(t)
# t+=0.02
# do0.go_high(t)
# # ai0.acquire(label='measurement1', start_time=t, end_time=t+0.01)
# t+=0.01
# do0.go_low(t)
# t += 0.05
# stop(t)