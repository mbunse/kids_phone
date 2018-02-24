#!/usr/bin/env python

import linphone
import logging
import signal
import time
import RPi.GPIO as GPIO
import phonebook
import threading

CRADLE_GPIO = 25
LINE_123 = 14
ROW_369 = 15
ROW_258 = 18
ROW_147 = 24
LINE_456 = 16
LINE_789 = 21
LINE_0 = 20
LINE_X = 26
LED = 7


class Kids_phone:
    def __init__(self):
        self.quit = False
        callbacks =  {'call_state_changed': self.call_state_changed}
 
        # Configure the linphone core
        logging.basicConfig(level=logging.INFO)
        signal.signal(signal.SIGINT, self.signal_handler)
        linphone.set_log_handler(self.log_handler)
        self.core = linphone.Core.new(callbacks, "/home/pi/.linphonerc", None)
        self.core.video_capture_enabled = False
        self.core.video_display_enabled = False
        self.core.max_calls = 1
        self.core.ringer_device='ALSA: bcm2835 ALSA'
        self.core.capture_device='ALSA: C-Media USB Headphone Set'
        self.core.playback_device='ALSA: C-Media USB Headphone Set'
        #self.core.ringer_device='ALSA: default device'
        self.core.ring='/usr/share/sounds/linphone/rings/oldphone.wav'

        self.state = linphone.CallState.Idle

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED, GPIO.OUT)
        GPIO.output(LED, False)
        self.blink_thread = threading.Thread(target=self.blink, args=(LED,))
        self.blink_event = threading.Event()
        self.blink_thread.start()

        #print "Sound: \n\n"
        #print self.core.sound_devices
        GPIO.setup(CRADLE_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.cradle_up = False
        # cradle is up when connection is closed, i.e. the state usually connected
        # to a button pressed down
        GPIO.add_event_detect(CRADLE_GPIO, GPIO.BOTH, callback=self.cradle_handler, bouncetime=20)

        self.button_123 = False
        self.button_369 = False
        self.button_258 = False
        self.button_147 = False
        self.button_456 = False
        self.button_789 = False
        self.button_0 = False
        GPIO.setup(LINE_123, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ROW_147, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ROW_258, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ROW_369, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(LINE_456, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(LINE_789, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(LINE_0, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(LINE_123, GPIO.BOTH, callback=self.button_123_handler, bouncetime=200)
        GPIO.add_event_detect(ROW_147, GPIO.BOTH, callback=self.button_147_handler, bouncetime=200)
        GPIO.add_event_detect(ROW_258, GPIO.BOTH, callback=self.button_258_handler, bouncetime=200)
        GPIO.add_event_detect(ROW_369, GPIO.BOTH, callback=self.button_369_handler, bouncetime=200)
        GPIO.add_event_detect(LINE_456, GPIO.BOTH, callback=self.button_456_handler, bouncetime=200)
        GPIO.add_event_detect(LINE_789, GPIO.BOTH, callback=self.button_789_handler, bouncetime=200)
        GPIO.add_event_detect(LINE_0, GPIO.BOTH, callback=self.button_0_handler, bouncetime=200)

        GPIO.setup(LINE_X, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(LINE_X, GPIO.BOTH, callback=self.button_x_handler, bouncetime=200)

    def signal_handler(self, signal, frame):
        logging.info("Terminating sigint")
        self.core.terminate_all_calls()
        self.quit = True
        try:
            sys.stdout.close()
        except:
            pass
        try:
            sys.stderr.close()
        except:
            pass
        self.blink_event.set()
        self.blink_thread.join()
        GPIO.cleanup()

    def log_handler(self, level, msg):
        method = getattr(logging, level)
        method(msg)
 
    def call_state_changed(self, core, call, state, message):
        self.state = state
        if state == linphone.CallState.IncomingReceived:
        # if call.remote_address.as_string_uri_only() in self.whitelist:
            logging.info("Anruf von {address}.".format(address=call.remote_address.as_string_uri_only()))
            if call.remote_address.username not in phonebook.WHITELIST:
                core.decline_call(call, linphone.Reason.Declined)
            #params = core.create_call_params(call)
            #core.accept_call_with_params(call, params)
        elif state == linphone.CallState.Released:
            self.core.terminate_all_calls()
        #    else:
        # core.decline_call(call, linphone.Reason.Declined)
        # chat_room = core.get_chat_room_from_uri(self.whitelist[0])
        # msg = chat_room.create_message(call.remote_address_as_string + ' tried to call')
        # chat_room.send_chat_message(msg)

    def cradle_handler(self, channel):
        if GPIO.input(channel) == False:
            #cradle up
            logging.info("Hoerer abgenommen")
            self.cradle_up = True
            # Accept incoming call if there is an incoming call
            if self.state == linphone.CallState.IncomingReceived:
                params = self.core.create_call_params(self.core.current_call)
                self.core.accept_call_with_params(self.core.current_call, params)
                self.blink_event.set()
        else:
            logging.info("Hoerer aufgelegt")
            self.cradle_up = False
            self.core.terminate_all_calls()
            self.blink_event.set()

    def button_123_handler(self, channel):
        if GPIO.input(channel) == False:
            # button down
            logging.debug("123 pressed")
            self.button_123 = True
            self.check_button()
        else:
            #button up
            logging.debug("123 released")
            self.button_123 = False

    def button_369_handler(self, channel):
        if GPIO.input(channel) == False:
            #button down:
            logging.debug("369 pressed")
            self.button_369 = True
            self.check_button()
        else:
            logging.debug("369 released")
            self.button_369 = False

    def button_258_handler(self, channel):
        if GPIO.input(channel) == False:
            #button down:
            logging.debug("258 pressed")
            self.button_258 = True
            self.check_button()
        else:        
            logging.debug("258 released")
            self.button_258 = False
        
    def button_147_handler(self, channel):
        if GPIO.input(channel) == False:
            #button down:
            logging.debug("147 pressed")
            self.button_147 = True
            self.check_button()
        else:
            logging.debug("147 released")
            self.button_147 = False

    def button_456_handler(self, channel):
        if GPIO.input(channel) == False:
            #button down:
            logging.debug("456 pressed")
            self.button_456 = True
            self.check_button()
        else:
            logging.debug("456 pressed")
            self.button_456 = False

    def button_789_handler(self, channel):
        if GPIO.input(channel) == False:
            #button down:
            logging.debug("789 pressed")
            self.button_789 = True
            self.check_button()
        else:
            logging.debug("789 released")
            self.button_789 = False

    def button_0_handler(self, channel):
        if GPIO.input(channel) == False:
            #button down:
            logging.debug("0 pressed")
            self.button_0 = True
            self.check_button()
        else:
            logging.debug("0 released")
            self.button_0 = False

    
    def button_x_handler(self, channel):
        if GPIO.input(channel) == False:
            #button down:
            logging.info("x pressed")
        else:
            logging.info("x released")

    def check_button(self):
        if self.button_123 and self.button_147:
            logging.info("1 pressed")
            self.button_123=False
            self.button_147=False
            self.call(1)
        elif self.button_123 and self.button_258:
            logging.info("2 pressed")
            self.button_123=False
            self.button_258=False
            self.call(2)
        elif self.button_123 and self.button_369:
            logging.info("3 pressed")
            self.button_123=False
            self.button_369=False
            self.call(3)
        elif self.button_456 and self.button_147:
            logging.info("4 pressed")
            self.button_456=False
            self.button_147=False
            self.call(4)
        elif self.button_456 and self.button_258:
            logging.info("5 pressed")
            self.button_456=False
            self.button_258=False
            self.call(5)
        elif self.button_456 and self.button_369:
            logging.info("6 pressed")
            self.button_456=False
            self.button_369=False
            self.call(6)
        elif self.button_789 and self.button_147:
            logging.info("7 pressed")
            self.button_789=False
            self.button_147=False
            self.call(7)
        elif self.button_789 and self.button_258:
            logging.info("8 pressed")
            self.button_789=False
            self.button_258=False
            self.call(8)
        elif self.button_789 and self.button_369:
            logging.info("9 pressed")
            self.button_789=False
            self.button_369=False
            self.call(9)
        elif self.button_0 and self.button_258:
            logging.info("0 pressed")
            self.button_0=False
            self.button_258=False
            self.call(0)

    def blink(self, channel):
        while self.quit == False:
            self.blink_event.clear()
            if self.state == linphone.CallState.IncomingReceived:
                GPIO.output(LED, True)
                if self.blink_event.wait(0.3) == True: 
                    continue 
                GPIO.output(LED, False)
                if self.blink_event.wait(0.2) == True: 
                    continue
            elif self.state in (linphone.CallState.OutgoingInit, 
                linphone.CallState.OutgoingProgress, 
                linphone.CallState.OutgoingRinging, 
                linphone.CallState.OutgoingEarlyMedia,
                linphone.CallState.Connected):
                GPIO.output(LED, True)
                if self.blink_event.wait(0.4) == True: 
                    continue 
                GPIO.output(LED, False)
                if self.blink_event.wait(0.1) == True: 
                    continue                
            else:    
                GPIO.output(LED, True)
                if self.blink_event.wait(0.5) == True:
                    continue 
                GPIO.output(LED, False)
                if self.blink_event.wait(5.0) == True:
                    continue 

    def call(self, number):
        if self.cradle_up == False:
            return
        # Call someone if there is no active call:
        if self.state in (linphone.CallState.Idle, linphone.CallState.Released, linphone.CallState.End):
            params = self.core.create_call_params(self.core.current_call)
            params.early_media_sending_enabled = False
            self.core.invite_with_params(phonebook.NUMBERS[number], params)
            self.blink_event.set()
  
    def run(self):
        while not self.quit:
            self.core.iterate()
            time.sleep(0.03)
   
def main():
    phone = Kids_phone()
    phone.run()
 
main()
