#!/usr/bin/env python

import linphone
import logging
import signal
import time
import RPi.GPIO as GPIO
import phonebook

CRADLE_GPIO = 25

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
        print "Device: \n\n"
        print self.core.ringer_device
        self.core.ringer_device='ALSA: bcm2835 ALSA'
        self.core.capture_device='ALSA: C-Media USB Headphone Set'
        self.core.playback_device='ALSA: C-Media USB Headphone Set'
        #self.core.ringer_device='ALSA: default device'
        self.core.ring='/usr/share/sounds/linphone/rings/oldphone.wav'
        #print "Sound: \n\n"
        #print self.core.sound_devices
        self.call = False
        self.state = linphone.CallState.Idle
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(CRADLE_GPIO, GPIO.IN)
        GPIO.add_event_detect(CRADLE_GPIO, GPIO.RISING, callback=self.cradle_handler)
 
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
            print "Es ruft jemand an"
            #params = core.create_call_params(call)
            #core.accept_call_with_params(call, params)
            self.call = True
        elif state == linphone.CallState.Idle:
            self.call = False
        elif state == linphone.CallState.Released:
            self.core.terminate_all_calls()
        #    else:
        # core.decline_call(call, linphone.Reason.Declined)
        # chat_room = core.get_chat_room_from_uri(self.whitelist[0])
        # msg = chat_room.create_message(call.remote_address_as_string + ' tried to call')
        # chat_room.send_chat_message(msg)
    def cradle_handler(self, channel):
            if self.state == linphone.CallState.IncomingReceived:
                params = self.core.create_call_params(self.core.current_call)
                self.core.accept_call_with_params(self.core.current_call, params)
                self.call = False
            elif self.state in (linphone.CallState.Idle, linphone.CallState.Released, linphone.CallState.End):
                params = self.core.create_call_params(self.core.current_call)
                self.core.invite_with_params(phonebook.NUMBER1, params)
            elif GPIO.input(CRADLE_GPIO)==True:
                self.core.terminate_all_calls()
  
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
