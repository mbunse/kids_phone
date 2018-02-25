#!/usr/bin/python

import linphone
import logging
import signal
import time
from os import environ

import RPi.GPIO as GPIO

import sqlite3

import fetap_keypad 
import cradle, blinker

BLINK_MODES = {
    "RUN": [0.5, 5],
    "INCOMING_CALL": [0.3, 0.2],
    "OUTGOING_CALL": [0.4, 0.1]
}

class Kids_phone:
    def __init__(self):
        self.quit = False
        callbacks =  {'call_state_changed': self.call_state_changed}
 
        # Configure the linphone core
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s:%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
        signal.signal(signal.SIGINT, self.signal_handler)
        linphone.set_log_handler(self.log_handler)
        if "LINPHONE_CFG" in environ:
            linphone_cfg=environ.get("LINPHONE_CFG")
        else:
            linphone_cfg="/home/pi/.linphonerc"
        self.core = linphone.Core.new(callbacks, linphone_cfg, None)
        self.core.video_capture_enabled = False
        self.core.video_display_enabled = False
        self.core.max_calls = 1
        self.core.ringer_device='ALSA: bcm2835 ALSA'
        self.core.capture_device='ALSA: C-Media USB Headphone Set'
        self.core.playback_device='ALSA: C-Media USB Headphone Set'
        #self.core.ringer_device='ALSA: default device'
        self.core.ring='/usr/share/sounds/linphone/rings/oldphone.wav'

        self.state = linphone.CallState.Idle

        # Setup blinker for LED
        blinker.setup_and_start(modes=BLINK_MODES)

        # Setup cradle handler
        cradle.setup(self.cradle_up_handler, self.cradle_down_handler)

        self.phonebook_db = sqlite3.connect('/home/pi/kids_phone_conf/db.kids_phone.sqlite', check_same_thread=False)
        fetap_keypad.setup(key_handler=self.call)

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

        # Stop blinking
        blinker.stop()
        # Free GPIO
        GPIO.cleanup()

        # Close db connection
        self.phonebook_db.close()

    def log_handler(self, level, msg):
        method = getattr(logging, level)
        method(msg)
 
    def call_state_changed(self, core, call, state, message):
        self.state = state
        if state == linphone.CallState.IncomingReceived:
        # if call.remote_address.as_string_uri_only() in self.whitelist:
            logging.info("Anruf von {address}.".format(address=call.remote_address.as_string_uri_only()))
            whitelist = [i[0] for i in self.phonebook_db.execute("select * from call_numbers_caller_number_allowed;").fetchall()]
            logging.info("Anruf von {address}.".format(address=call.remote_address.as_string_uri_only()))
            logging.info("Erlaubte Nummern: " + ", ".join(whitelist))
            if call.remote_address.username not in whitelist:
                core.decline_call(call, linphone.Reason.Declined)

            blinker.set_mode("INCOMING_CALL")
        elif state == linphone.CallState.Released:
            self.core.terminate_all_calls()
            blinker.set_mode("RUN")
        elif self.state in (linphone.CallState.OutgoingInit, 
                linphone.CallState.OutgoingProgress, 
                linphone.CallState.OutgoingRinging, 
                linphone.CallState.OutgoingEarlyMedia,
                linphone.CallState.Connected):
                blinker.set_mode("OUTGOING_CALL")
        else:
            blinker.set_mode("RUN")

    def cradle_up_handler(self):
        # Accept incoming call if there is an incoming call
        if self.state == linphone.CallState.IncomingReceived:
            params = self.core.create_call_params(self.core.current_call)
            self.core.accept_call_with_params(self.core.current_call, params)
    
    def cradle_down_handler(self):
        self.core.terminate_all_calls()

    def call(self, number):
        if cradle.check_cradle() == False:
            return
        # Call someone if there is no active call:
        if self.state in (linphone.CallState.Idle, linphone.CallState.Released, linphone.CallState.End):
            # Check if phonenumber is set for current key
            phonenumber = self.phonebook(number)
            if phonenumber != None:
                params = self.core.create_call_params(self.core.current_call)
                params.early_media_sending_enabled = False
                self.core.invite_with_params(phonenumber, params)
    
    def phonebook(self, number):
        number = self.phonebook_db.execute(
            'select phonenumber from call_numbers_key_and_number where key=?', str(number)).fetchone()[0]
        return str(number)
  
    def run(self):
        while not self.quit:
            self.core.iterate()
            time.sleep(0.03)
   
def main():
    phone = Kids_phone()
    phone.run()
 
main()
