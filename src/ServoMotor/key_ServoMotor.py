import curses
import pigpio
from time import sleep

# Make BCM assignments for servo motors
servo_tilt = 17
servo_pan = 18

# Get the curses window, turn off echoing of keyboard to screen, turn on
# instant (no waiting) key response, and use special values for cursor keys
screen = curses.initscr()
curses.noecho() 
curses.cbreak()
screen.keypad(True)

# PWM frequency for servos
pwm_freq_hz = 50

# Pulse widths for servos
OFF_WIDTH_USEC    = 0
#MIN_WIDTH_USEC    = 500
#CENTER_WIDTH_USEC = 1500
#MAX_WIDTH_USEC    = 2500
TILT_MIN_WIDTH_USEC    = 850
TILT_CENTER_WIDTH_USEC = 1500
TILT_MAX_WIDTH_USEC    = 2000
PAN_MIN_WIDTH_USEC    = 1250
PAN_CENTER_WIDTH_USEC = 1500
PAN_MAX_WIDTH_USEC    = 1950

# Step size for incremental servo position
SERVO_STEP = 4

# Create a pigpio object
pi = pigpio.pi()

# Exit if the pigpio demon is not running
if not pi.connected:
    exit()

# Set the frequency for the two servo channels
servo_tilt_freq = pi.set_PWM_frequency(servo_tilt, pwm_freq_hz)
servo_pan_freq = pi.set_PWM_frequency(servo_pan, pwm_freq_hz)
print(f"Servo tilt freq: {servo_tilt_freq}")
print(f"Servo pan freq: {servo_pan_freq}")

# Current positions of the pan and tilt servo as well as the joystick
current_tilt_pos = TILT_CENTER_WIDTH_USEC
current_pan_pos = PAN_CENTER_WIDTH_USEC
pi.set_servo_pulsewidth(servo_tilt, TILT_CENTER_WIDTH_USEC)
pi.set_servo_pulsewidth(servo_pan, PAN_CENTER_WIDTH_USEC)

try:
    while True:   
        char = screen.getch()
        if char == ord('q'):
            break
        elif char == curses.KEY_UP:
            print("KEY_UP")
            if current_tilt_pos < TILT_MAX_WIDTH_USEC:
                current_tilt_pos += SERVO_STEP
                if current_tilt_pos > TILT_MAX_WIDTH_USEC:
                    current_tilt_pos = TILT_MAX_WIDTH_USEC
                print(current_tilt_pos)
                pi.set_servo_pulsewidth(servo_tilt, current_tilt_pos)
        elif char == curses.KEY_DOWN:
            print("KEY_DOWN")
            if current_tilt_pos > TILT_MIN_WIDTH_USEC:
                current_tilt_pos -= SERVO_STEP
                if current_tilt_pos < TILT_MIN_WIDTH_USEC:
                    current_tilt_pos = TILT_MIN_WIDTH_USEC
                print(current_tilt_pos)
                pi.set_servo_pulsewidth(servo_tilt, current_tilt_pos)
        elif char == curses.KEY_RIGHT:
            print("KEY_RIGHT")
            if current_pan_pos > PAN_MIN_WIDTH_USEC:
                current_pan_pos -= SERVO_STEP
                if current_pan_pos < PAN_MIN_WIDTH_USEC:
                    current_pan_pos = PAN_MIN_WIDTH_USEC
                print(current_pan_pos)
                pi.set_servo_pulsewidth(servo_pan, current_pan_pos)
        elif char == curses.KEY_LEFT:
            print("KEY_LEFT")
            if current_pan_pos < PAN_MAX_WIDTH_USEC:
                current_pan_pos += SERVO_STEP
                if current_pan_pos > PAN_MAX_WIDTH_USEC:
                    current_pan_pos = PAN_MAX_WIDTH_USEC
                print(current_pan_pos)
                pi.set_servo_pulsewidth(servo_pan, current_pan_pos)
        elif char == 10:
            print("ENTER")
            pi.set_servo_pulsewidth(servo_tilt, TILT_CENTER_WIDTH_USEC)
            pi.set_servo_pulsewidth(servo_pan, PAN_CENTER_WIDTH_USEC)
            current_tilt_pos = TILT_CENTER_WIDTH_USEC
            current_pan_pos = PAN_CENTER_WIDTH_USEC
            
# Prevent Traceback warning when using Ctrl-C to exit the program
except KeyboardInterrupt:
    pass # no-op
                 
finally:
    #Close down curses properly, inc turn echo back on!
    print("Cleaning up ...")
    print(TILT_CENTER_WIDTH_USEC)
    sleep(2)
    pi.set_servo_pulsewidth(servo_tilt, OFF_WIDTH_USEC)               
    pi.set_servo_pulsewidth(servo_pan, OFF_WIDTH_USEC)               
    pi.stop()
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()
