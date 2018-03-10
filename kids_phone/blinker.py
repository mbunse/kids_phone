import RPi.GPIO as GPIO
import logging
import threading

__modes = None
__mode = None
__blink_event = None
__blink_thread = None
__quit_mode = "QUIT"
LED = 7

def setup_and_start(modes={}, inital_mode="RUN", quit_mode="QUIT"):
    global __modes, __mode, __blink_event, __blink_thread, __quit_mode
    if __modes is None:
        __modes = modes
    else:
        raise RuntimeError("Modes have already been set.")

    __quit_mode = quit_mode
    __mode = inital_mode

    if GPIO.getmode() == None:
        GPIO.setmode(GPIO.BCM)

    GPIO.setup(LED, GPIO.OUT)
    GPIO.output(LED, False)

    __blink_thread = threading.Thread(target=blink, args=(LED,))
    __blink_event = threading.Event()
    __blink_thread.start()


def blink(channel):
    
    def blink_step():
        global __modes, __mode, __blink_event
        next_state = True
        logging.debug("current mode is {mode}".format(mode=__mode))
        for mode_blink_step in __modes[__mode]:
            GPIO.output(LED, next_state)
            next_state = not next_state
            if __blink_event.wait(mode_blink_step) == True: 
                return

    global __mode, __blink_event, __quit_mode
    while True:
        __blink_event.clear()
        if __mode == __quit_mode:
            break
        blink_step()
def stop():
    global __blink_event, __blink_thread, __mode
    __mode = __quit_mode

    # Inform blink thread that app will be quit
    __blink_event.set()

    # Wait for blink thread to exit
    __blink_thread.join()

def set_mode(mode):

    global __blink_event, __mode
    __mode = mode
    __blink_event.set()
    
if __name__=="__main__":
    import time
    logging.basicConfig(level=logging.DEBUG)
    
    setup_and_start(modes={"RUN":[0.5, 0.5]})
    time.sleep(4)
    stop()