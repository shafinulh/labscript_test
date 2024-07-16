from labscript import *
from labscript_devices.PulseBlasterUSB import PulseBlasterUSB
from labscript_devices.PineBlaster import PineBlaster
from labscript_devices.NI_DAQmx.labscript_devices import NI_PCIe_6363
from labscript_devices.FunctionRunner.labscript_devices import FunctionRunner

'''
Initialize the FunctionRunner that runs scripts before and after shots
'''
FunctionRunner(name='feedback1')

'''
Initialize the PulseBlaster as the Pseudoclock
and all the channels to be used
'''
# PulseBlasterUSB(name='pb',board_number=0,programming_scheme='pb_start/BRANCH')
# ClockLine(name='pb_clockline_fast', pseudoclock=pb.pseudoclock,connection='flag 0')
PineBlaster(name='pb', usbport='COM3')
# ClockLine(name='pb_clockline_fast', pseudoclock=pb.pseudoclock,connection='flag 0')

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
AnalogIn(name="ai2", parent_device=ni_6363, connection='ai2')
AnalogIn(name="ai3", parent_device=ni_6363, connection='ai3')

'''
Define the Experiment Logic
'''
def digital_start_ref():
    t=0
    do1.go_high(t)
    t+=10e-3
    do1.go_low(t)
    return t
def digital_pwm_stream():
    t=ctrl_pwm_ti
    add_time_marker(t, "D0 PWM CTRL")
    while t<=ctrl_pwm_tf:
        do0.go_high(t)
        t+=((1/ctrl_pwm_freq) * ctrl_duty_cycle)
        do0.go_low(t)
        t+=((1/ctrl_pwm_freq) * (1-ctrl_duty_cycle))
    return t
def analog_output_ramp():
    t=ramp_ti
    add_time_marker(t, "A0 Ramp", verbose=True)
    t+=ao0.ramp(
        t=t, 
        initial=ramp_vi, 
        final=ramp_vf, 
        duration=ramp_dur, 
        samplerate=ramp_rate
    )
    ao0.constant(t=t, value=(ramp_vf+ramp_vi)/2)
    return t
def analog_output_exp_ramp():
    t=exp_ramp_ti
    add_time_marker(t, "A1 Fast Exp Ramp", verbose=True)
    t+=ao1.exp_ramp_t(
        t=t, 
        initial=exp_ramp_vi, 
        final=exp_ramp_vf, 
        duration=exp_ramp_dur, 
        samplerate=exp_ramp_rate, 
        time_constant=exp_ramp_time_const,
    )
    ao1.constant(t=t, value=(exp_ramp_vf+exp_ramp_vi)/2)
    return t

def collect_AO_0():
    t=ramp_ti
    t+=ai0.acquire(label='AO_ramp', start_time=t, end_time=ramp_tf)
    
    # t+= 10e-3
    # ai0.acquire(label='dummy_measurement_AO_0_fast', start_time=t, end_time=t+3e-3)
    # t+=3e-3
    return t
def collect_AO_1():
    t=exp_ramp_ti
    t+=ai1.acquire(label='AI_signal', start_time=t, end_time=exp_ramp_tf)
    
    # t=45e-3
    # ai1.acquire(label='dummy_measurement_AO_1_fast', start_time=t, end_time=t+3e-3)
    # t+=3e-3
    return t
def collect_dummy_inputs():
    t=62e-3
    ai2.acquire(label='dummy_measurement_slow', start_time=t, end_time=t+20e-3)
    t+=20e-3
    t+=5e-3
    ai3.acquire(label='dummy_measurement_med', start_time=t, end_time=t+13e-3)
    t+=13e-3
    return t

t=0
start()
t=max(t, digital_start_ref())
t=max(t, digital_pwm_stream())
t=max(t, analog_output_ramp())
t=max(t, analog_output_exp_ramp())
t=max(t, collect_AO_0())
t=max(t, collect_AO_1())
# t=max(t, collect_dummy_inputs())
print(t)
stop(t)

