#!/usr/bin/env python

import linphone
import logging
import signal
import time
import RPi.GPIO as GPIO
import phonebook

CRADLE_GPIO = 25
LINE_123 = 14
ROW_369 = 15
ROW_258 = 18
ROW_147 = 24

class Kids_phone:
    def __init__(self):
        self.quit = False
        callbacks =  {'call_state_changed': self.call_state_changed}
 
        # Configure the linphone core
        logging.basicConfig(level=logging.WARNING)
        signal.signal(signal.SIGINT, self.signal_handler)
        linphone.set_log_handler(self.log_handler)
        self.core = linphone.Core.new(callbacks, "/home/pi/.linphonerc", None)
        self.core.video_capture_enabled = False
        self.core.video_display_enabled = False
        self.core.max_calls = 1
        print "Device: \n\n"
        print self.core.ringer_device
        self.core.ringer_device='ALSA: bcm2835 ALSA'
        self.core.capture_device='ALSA: C-Media USB Headphone Set'
        self.core.playback_device='ALSA: C-Media USB Headphone Set'
        #self.core.ringer_device='ALSA: default device'
        self.core.ring='/usr/share/sounds/linphone/rings/oldphone.wav'
        #print "Sound: \n\n"
        #print self.core.sound_devices
        self.state = linphone.CallState.Idle
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CRADLE_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.cradle_up = False
        # cradle is up when connection is closed, i.e. the state usually connected
        # to a button pressed down
        GPIO.add_event_detect(CRADLE_GPIO, GPIO.BOTH, callback=self.cradle_handler, bouncetime=200)

        self.button_123 = False
        self.button_369 = False
        self.button_258 = False
        self.button_147 = False
        GPIO.setup(LINE_123, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ROW_147, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ROW_258, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(ROW_369, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(LINE_123, GPIO.BOTH, callback=self.button_123_handler, bouncetime=200)
        GPIO.add_event_detect(ROW_147, GPIO.BOTH, callback=self.button_147_handler, bouncetime=200)
        GPIO.add_event_detect(ROW_258, GPIO.BOTH, callback=self.button_258_handler, bouncetime=200)
        GPIO.add_event_detect(ROW_369, GPIO.BOTH, callback=self.button_369_handler, bouncetime=200)

    def signal_handler(self, signal, frame):
        print "Terminating sigint"
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
 
    def log_handler(self, level, msg):
        method = getattr(logging, level)
        method(msg)
 
    def call_state_changed(self, core, call, state, message):
        self.state = state
        if state == linphone.CallState.IncomingReceived:
        # if call.remote_address.as_string_uri_only() in self.whitelist:
            loggin.info("Es ruft jemand an")
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
        else:
            logging.info("Hoerer aufgelegt")
            self.cradle_up = False
            self.core.terminate_all_calls()

    def button_123_handler(self, channel):
        if GPIO.input(channel) == False:
            # button down
            logging.info("123 pressed")
            self.button_123 = True
            self.check_button()
        else:
            #button up
            logging.info("123 released")
            self.button_123 = False

    def button_369_handler(self, channel):
        if GPIO.input(channel) == False:
            #button down:
            logging.info("369 pressed")
            self.button_369 = True
            self.check_button()
        else:
            logging.info("369 released")
            self.button_369 = False

    def button_258_handler(self, channel):
        if GPIO.input(channel) == False:
            #button down:
            logging.info("258 pressed")
            self.button_258 = True
            self.check_button()
        else:        
            logging.info("258 released")
            self.button_258 = False
        
    def button_147_handler(self, channel):
        if GPIO.input(channel) == False:
            #button down:
            logging.info("147 pressed")
            self.button_147 = True
            self.check_button()
        else:
            logging.info("147 released")
            self.button_147 = False

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
            #self.call(2)
        elif self.button_123 and self.button_369:
            logging.info("3 pressed")
            self.button_123=False
            self.button_369=False
            #self.call(3)

    def call(self, number):
        if self.cradle_up == False:
            return
        # Call someone if there is no active call:
        if self.state in (linphone.CallState.Idle, linphone.CallState.Released, linphone.CallState.End):
            params = self.core.create_call_params(self.core.current_call)
            self.core.invite_with_params(phonebook.NUMBERS[number], params)
  
    def run(self):
        try:
            while not self.quit:
                self.core.iterate()
                time.sleep(0.03)
        except KeyboardInterrupt:
            print "Terminating KeyboardInterrupt"
            self.core.terminate_all_calls()
            self.quit = True

   
def main():
    phone = Kids_phone()
    phone.run()
 
main()
