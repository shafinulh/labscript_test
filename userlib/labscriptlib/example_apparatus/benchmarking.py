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
PrawnBlaster(
    name='pb',
    com_port='COM5',
    num_pseudoclocks=2
)

'''
Initialize the NI Hardware and all the channels
to be used on each card
'''
ni_6361_max_name = "PXI1Slot8"
NI_PXIe_6361(
    name='ni_6361_mio', 
    parent_device=pb_clock_line_1,
    clock_terminal=f'/{ni_6361_max_name}/PFI1',
    MAX_name=f'{ni_6361_max_name}',
    acquisition_rate=250e3,
)
AnalogOut(name='ao0_6361', parent_device=ni_6361_mio, connection='ao0')
AnalogOut(name='ao1_6361', parent_device=ni_6361_mio, connection='ao1')
DigitalOut(name='do0_6361', parent_device=ni_6361_mio, connection='port0/line0')
DigitalOut(name='do1_6361', parent_device=ni_6361_mio, connection='port0/line1')
AnalogIn(name='ai0_6361', parent_device=ni_6361_mio, connection='ai0')
AnalogIn(name='ai1_6361', parent_device=ni_6361_mio, connection='ai1')


ni_6739_max_name = "PXI1Slot3"
NI_PXIe_6739(
    name='ni_6739_ao', 
    parent_device=pb_clock_line_0,
    clock_terminal=f'/{ni_6739_max_name}/PFI0',
    MAX_name=f'{ni_6739_max_name}',
)
AnalogOut(name='ao0_6739', parent_device=ni_6739_ao, connection='ao0')
AnalogOut(name='ao1_6739', parent_device=ni_6739_ao, connection='ao4')
AnalogOut(name='ao2_6739', parent_device=ni_6739_ao, connection='ao8')
AnalogOut(name='ao3_6739', parent_device=ni_6739_ao, connection='ao12')

'''
Define the Experiment Logic
'''
def digital_start_ref():
    t=0
    do1_6361.go_high(t)
    t+=10e-3
    do1_6361.go_low(t)
    return t

def digital_pwm_stream():
    t=ctrl_pwm_ti
    # add_time_marker(t, "D0 PWM CTRL")
    while t<=ctrl_pwm_tf:
        do0_6361.go_high(t)
        t+=((1/ctrl_pwm_freq) * ctrl_duty_cycle)
        do0_6361.go_low(t)
        t+=((1/ctrl_pwm_freq) * (1-ctrl_duty_cycle))
    return t

def analog_output_ramp():
    t=ramp_ti
    ao0_6361.constant(t=0, value=0)
    # add_time_marker(t, "A0 Ramp", verbose=True)
    t+=ao0_6361.ramp(
        t=t, 
        initial=ramp_vi, 
        final=ramp_vf, 
        duration=ramp_dur, 
        samplerate=ramp_rate
    )
    ao0_6361.constant(t=t, value=(ramp_vf/2))
    return t

def analog_output_exp_ramp():
    t=0
    ao1_6361.constant(t=t, value=exp_ramp_vi)
    t=exp_ramp_ti
    t+=ao1_6361.sine4_reverse_ramp(
        t=t,
        initial=exp_ramp_vf,
        final=exp_ramp_vi,
        duration=exp_ramp_dur_1,
        samplerate=exp_ramp_rate,
        truncation=0.8
    )
    t+=ao1_6361.sine_ramp(
        t=t,
        initial=exp_ramp_vf,
        final=exp_ramp_vi,
        duration=exp_ramp_dur_2,
        samplerate=exp_ramp_rate,
    )
    return t

def collect_AO_0():
    t=ramp_ti
    t+=ai0_6361.acquire(label='AO_ramp', start_time=t, end_time=exp_ramp_tf)
    return t

def collect_AO_1():
    t=exp_ramp_ti
    t+=ai1_6361.acquire(label='AI_signal', start_time=0, end_time=exp_ramp_tf)
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
