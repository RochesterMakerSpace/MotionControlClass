from machine import Pin
from rp2 import PIO, StateMachine, asm_pio
from time import sleep
import sys


# Return string of an integer formatted in binary
def bin_nibble(a, pad=4):
    b = '{:b}'.format(a)
    if len(b) % pad:
        b = '0' * (pad - (len(b) % pad)) + b
    return '_'.join(b[k:k+pad] for k in range(0, len(b), pad))


# Rotate a list
def rotate(l, n):
    return l[n:] + l[:n]


# CWW state machine. Same as CW except for shift direction
@asm_pio(set_init=(PIO.OUT_LOW,) * 4,
         out_init=(PIO.OUT_LOW,) * 4,
         out_shiftdir=PIO.SHIFT_LEFT) # CCW
#         out_shiftdir=PIO.SHIFT_RIGHT) #CW
def prog_ccw():
    pull()
    mov(x, osr) # num steps
    
    pull()
    mov(y, osr) # step pattern
    
    jmp(not_x, "end")
    
    label("loop")
    jmp(not_osre, "step") # loop pattern if exhausted
    mov(osr, y)
    
    label("step")
    out(pins, 4) [31]
    
    jmp(x_dec,"loop")
    label("end")
    
    irq(rel(0))


# CW state machine. Same as CCW except for shift direction
@asm_pio(set_init=(PIO.OUT_LOW,) * 4,
         out_init=(PIO.OUT_LOW,) * 4,
#         out_shiftdir=PIO.SHIFT_LEFT) # CCW
         out_shiftdir=PIO.SHIFT_RIGHT) #CW
def prog_cw():
    pull()
    mov(x, osr) # num steps
    
    pull()
    mov(y, osr) # step pattern
    
    jmp(not_x, "end")
    
    label("loop")
    jmp(not_osre, "step") # loop pattern if exhausted
    mov(osr, y)
    
    label("step")
    out(pins, 4) [31]
    
    jmp(x_dec,"loop")
    label("end")
    
    irq(rel(0))

sm_ccw = StateMachine(0, prog_ccw, freq=10000, set_base=Pin(2), out_base=Pin(2))
sm_cw = StateMachine(1, prog_cw, freq=10000, set_base=Pin(2), out_base=Pin(2))

# Pin sequences
step_mode = 'full_step'
if step_mode == 'half_step':
    data = [0b1000,
            0b1100,
            0b0100,
            0b0110,
            0b0010,
            0b0011,
            0b0001,
            0b1001]
elif step_mode == 'full_step': # Full step - Two phase ON
    data = [0b1100,
            0b0110,
            0b0011,
            0b1001]
else: # Full step - One phase ON
    data = [0b1000,
            0b0100,
            0b0010,
            0b0001]
        
steps = 0 # Accumulator for number of steps to sequence the next turn at the proper place in the sequence
num_steps = 2038 # One revolution in full step mode. 1/2 half revolution in half step mode


# Process the interrupt from the state machines. If done with CW then turn CCW and vise versa.
def handler(sm):
    # Print the state machine object.
    print(sm)
    if sm == sm_cw:
        turn(sm_ccw)
    else:
        turn(sm_cw)


# Turn the motor by sending the SM the number of steps
# and the sequence of pin settings. The rotate is necessary
# pick up the sequence where the last turn left the motor.
def turn(sm):
    global steps
    global data
    global num_steps
    
    idx = steps % 4
    rdata = rotate(data, idx)    
    if step_mode == 'half_step':
        a = rdata[0] | (rdata[1] << 4) | (rdata[2] << 8) | (rdata[3] << 12) | (rdata[4] << 16) | (rdata[5] << 20) | (rdata[6] << 24) | (rdata[7] << 28)
    else: #both types of full step (one phase and two phase)
        a = rdata[0] | (rdata[1] << 4) | (rdata[2] << 8) | (rdata[3] << 12)
        a = a << 16 | a
    
    print(bin_nibble(a))
    sleep(1)
    
    sm.put(num_steps)
    sm.put(a)
    
    steps += num_steps

# Activate the state machines and start turning
sm_cw.irq(handler)
sm_cw.active(1)
sm_ccw.irq(handler)
sm_ccw.active(1)
turn(sm_cw)

# Stop turning after 50 seconds and clean up
print("sleeping")
sleep(50)
print("done")
sm_cw.active(0)
sm_cw.exec("set(pins,0)")
sm_ccw.active(0)
sm_ccw.exec("set(pins,0)")





