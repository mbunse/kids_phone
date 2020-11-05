"""
Module to handle Fetap Keypad.

Global Variables
================
`COLS_AND_ROWS`:    List of two list with
                    GPIO pins for columns and
                    rows of key pad
"""
import RPi.GPIO as GPIO
import logging
from itertools import compress
import time

ROW_PINS = [22, 10, 9, 11]
COL_PINS = [4, 17, 27]

TWB75 = 1
TWB81 = 0
__key_handler = None
__twb_type = None

STATE = {False: "False", True: "True"}

def setup(key_handler, twb_type = TWB81):
    """
    Parameters
    ==========
    key_handler: function of pressed key (integer) called
        when a key is pressed
    """
    logging.debug("intializing {name}".format(name=__file__))

    global __key_handler, __twb_type
    if __key_handler is None:
        __key_handler = key_handler
    else:
        raise RuntimeError("Key handler has already been set.")

    if __twb_type is None:
        __twb_type = twb_type
    else:
        raise RuntimeError("TWB tpye has already been set.")

    global __active_rows, __active_cols
    __active_rows = [False, False, False, False]
    __active_cols = [False, False, False]
    if GPIO.getmode() == None:
        GPIO.setmode(GPIO.BCM)
    if __twb_type == TWB81:
        for pin in ROW_PINS+COL_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=pin_handler)
    elif __twb_type == TWB75:
        for pin in ROW_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        for pin in COL_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=pin_handler)
    else:
        raise ValueError("twb_type should be either fetap_keypad.TWB75 or fetap_keypad.TWB81.")
def cleanup():
    global __key_handler, __twb_type
    __key_handler = None
    __twb_type = None
    logging.debug("cleaning up {name}".format(name=__file__))
    #GPIO.cleanup(ROW_PINS+COL_PINS)
    GPIO.cleanup()
    return

def pin_handler(pin):
    global __active_rows, __active_cols
    logging.debug("pin_handler called")

    row, col = get_row_col_from_pin(pin)
    if GPIO.input(pin) == False:
        #button down:
        if col != None:
            logging.debug("column {col} pressed.".format(col=col))
            __active_cols[col] = True
        elif row != None:
            logging.debug("row {row} pressed.".format(row=row))
            __active_rows[row] = True
        check_button()
    else:
        if col != None:
            logging.debug("column {col} released.".format(col=col))
            __active_cols[col] = False
        elif row != None:
            logging.debug("row {row} released.".format(row=row))
            __active_rows[row] = False

def get_row_col_from_pin(pin):
    row, col = (None,None)
    for idx, ipin in enumerate(ROW_PINS+COL_PINS):
        if ipin==pin:
            # Floor division
            if (idx // 4) == 0:
                row=idx % 4
            else:
                col=idx % 4
            return row, col
    return row, col

def check_button():
    global __active_rows, __active_cols, __twb_type

    if __twb_type == TWB75:
        # Switch the i-th row found from scan to output
        for pin in ROW_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Switch pin to output for active column
        for pin in compress(COL_PINS, __active_cols):
            #GPIO.remove_event_detect(pin)
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)
            

        for pin in ROW_PINS:
            if GPIO.input(pin):
                row, _ = get_row_col_from_pin(pin)
                __active_rows[row] = True
                # Wait for release of button
                GPIO.wait_for_edge(pin, GPIO.FALLING, timeout=2000)

                # Avoid bouncing
                while GPIO.input(pin):
                    time.sleep(0.02)
                break
        
        # Reset state        
        for pin in compress(COL_PINS, __active_cols):
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            #GPIO.add_event_detect(pin, GPIO.BOTH, callback=pin_handler)
        for pin in ROW_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

    #Check if two pins are active. If not, exit function
    if min(1,sum(__active_rows))+min(1,sum(__active_cols))<2:
        return

    # Check which row and col is pressed
    colidx = None
    rowidx = None
    for idx, isactive in enumerate(__active_rows):
        if isactive:
            rowidx=idx
            break
    for idx, isactive in enumerate(__active_cols):
        if isactive:
            colidx=idx
            break

    # Reset col and rows
    __active_rows = [False, False, False, False]
    __active_cols = [False, False, False]

    pressed_key = rowidx*3+colidx+1
    if pressed_key==11: 
        pressed_key=0

    logging.info("{pressed_key} pressed".format(pressed_key=pressed_key))
    __key_handler(pressed_key)

if __name__=="__main__":
    import time
    logging.basicConfig(level=logging.DEBUG)
    def key_handler(key):
        print("{key} pressed".format(key=key))
    
    setup(key_handler=key_handler, twb_type=TWB75)
    time.sleep(200)
    cleanup()