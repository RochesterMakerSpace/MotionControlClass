# import curses and GPIO
import curses
import RPi.GPIO as GPIO
from time import sleep

# Make BCM assignments
in1 = 26
in2 = 19
in3 = 20
in4 = 16

#set GPIO numbering mode and define output pins
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(in3,GPIO.OUT)
GPIO.setup(in4,GPIO.OUT)

# Get the curses window, turn off echoing of keyboard to screen, turn on
# instant (no waiting) key response, and use special values for cursor keys
screen = curses.initscr()
curses.noecho() 
curses.cbreak()
screen.keypad(True)

GPIO.output(in1,False)
GPIO.output(in2,False)
GPIO.output(in3,False)
GPIO.output(in4,False)

try:
    while True:   
        char = screen.getch()
        if char == ord('q'):
            break
        elif char == curses.KEY_UP:
            print("KEY_UP")
            GPIO.output(in1,False)
            GPIO.output(in2,True)
            GPIO.output(in3,False)
            GPIO.output(in4,True)
        elif char == curses.KEY_DOWN:
            print("KEY_DOWN")
            GPIO.output(in1,True)
            GPIO.output(in2,False)
            GPIO.output(in3,True)
            GPIO.output(in4,False)
        elif char == curses.KEY_RIGHT:
            print("KEY_RIGHT")
            GPIO.output(in1,True)
            GPIO.output(in2,False)
            GPIO.output(in3,False)
            GPIO.output(in4,True)
        elif char == curses.KEY_LEFT:
            print("KEY_LEFT")
            GPIO.output(in1,False)
            GPIO.output(in2,True)
            GPIO.output(in3,True)
            GPIO.output(in4,False)
        elif char == 10:
            print("ENTER")
            GPIO.output(in1,False)
            GPIO.output(in2,False)
            GPIO.output(in3,False)
            GPIO.output(in4,False)
            
# Prevent Traceback warning when using Ctrl-C to exit the program
except KeyboardInterrupt:
    pass # no-op
                 
finally:
    #Close down curses properly, inc turn echo back on!
    print("Cleaning up ...")
    sleep(1)
    curses.nocbreak(); screen.keypad(0); curses.echo()
    curses.endwin()
    GPIO.cleanup()
    

