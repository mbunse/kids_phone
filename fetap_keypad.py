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


ROW_PINS = [14, 16, 21, 20]
COL_PINS = [24, 18, 15]

__key_handler = None

def setup(key_handler):
    """
    Parameters
    ==========
    key_handler: function of pressed key (integer) called
        when a key is pressed
    """
    logging.debug("intializing {name}".format(name=__file__))

    global __key_handler 
    if __key_handler is None:
        __key_handler = key_handler
    else:
        raise RuntimeError("Key handler has already been set.")

    global __active_rows, __active_cols
    __active_rows = [False, False, False, False]
    __active_cols = [False, False, False]
    if GPIO.getmode() == None:
        GPIO.setmode(GPIO.BCM)
    for pin in ROW_PINS+COL_PINS:
        if pin:
            logging.debug("Setting up pin {pin}".format(pin=pin))
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=pin_handler, bouncetime=200)
def cleanup():
    logging.debug("cleaning up {name}".format(name=__file__))
    #GPIO.cleanup(ROW_PINS+COL_PINS)
    GPIO.cleanup()
    return

def pin_handler(pin):
    global __active_rows, __active_cols

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
    global __active_rows, __active_cols

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
    
    setup(key_handler=key_handler)
    time.sleep(200)
    cleanup()