#!/usr/bin/python

import linphone
import logging
import signal
import time
import RPi.GPIO as GPIO

import threading
import sqlite3

from fetap_keypad import Fetap_Keypad 

CRADLE_GPIO = 25
LED = 7


class Kids_phone:
    def __init__(self):
        self.quit = False
        callbacks =  {'call_state_changed': self.call_state_changed}
 
        # Configure the linphone core
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s:%(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
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

        self.phonebook_db = sqlite3.connect('/home/pi/kids_phone_conf/db.kids_phone.sqlite', check_same_thread=False)
        self.keypad = Fetap_Keypad(key_handler=self.call)

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
        # Inform blink thread that app will be quit
        self.blink_event.set()

        # Wait for blink thread to exit
        self.blink_thread.join()

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
            # Check if phonenumber is set for current key
            phonenumber = self.phonebook(number)
            if phonenumber != None:
                params = self.core.create_call_params(self.core.current_call)
                params.early_media_sending_enabled = False
                self.core.invite_with_params(phonenumber, params)

                # Inform blink thread that state has been changed
                self.blink_event.set()
    
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
