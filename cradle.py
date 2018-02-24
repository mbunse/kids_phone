"""
Module to handle cradle.

Global Variables
================
`CRADLE_GPIO`:    GPIO pins for cradle 
"""
import RPi.GPIO as GPIO
import logging

CRADLE_GPIO = 25

__cradle_up = False
__cradle_up_handler = None
__cradle_down_handler = None

def setup(cradle_up_handler, cradle_down_handler):
    logging.debug("intializing {name}".format(name=__file__))
    global __cradle_up, __cradle_up_handler, __cradle_down_handler
    __cradle_up = False
    __cradle_up_handler = None
    if __cradle_up_handler is None:
        __cradle_up_handler = cradle_up_handler
    else:
        raise RuntimeError("Cradle up handler has already been set.")
    __cradle_down_handler = None
    if __cradle_down_handler is None:
        __cradle_down_handler = cradle_down_handler
    else:
        raise RuntimeError("Cradle down handler has already been set.")
    if GPIO.getmode() == None:
        GPIO.setmode(GPIO.BCM)

    GPIO.setup(CRADLE_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # cradle is up when connection is closed, i.e. the state usually connected
    # to a button pressed down
    GPIO.add_event_detect(CRADLE_GPIO, GPIO.BOTH, callback=cradle_handler, bouncetime=20)

def cleanup():
    logging.debug("cleaning up {name}".format(name=__file__))
    #GPIO.cleanup(ROW_PINS+COL_PINS)
    GPIO.cleanup()
    return

def cradle_handler(channel):
    global __cradle_up, __cradle_up_handler, __cradle_down_handler
    if GPIO.input(channel) == False:
        #cradle up
        logging.info("Cradle up")
        __cradle_up = True
        __cradle_up_handler()
    else:
        logging.info("Cradle down")
        __cradle_up = False
        __cradle_down_handler()

def check_cradle():
    global __cradle_up
    return __cradle_up

if __name__=="__main__":
    import time
    logging.basicConfig(level=logging.DEBUG)
    def cradle_down_handler():
        print("cradle down")

    def cradle_up_handler():
        print("cradle up")
    
    setup(cradle_up_handler, cradle_down_handler)
    time.sleep(10)
    cleanup()