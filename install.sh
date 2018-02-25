#!/bin/bash

# create dedicated user
useradd -r -s /bin/false kids_phone
# Add user to gpio group to grand access to /dev/mem
adduser kids_phone gpio
# Grant access to audio
adduser kids_phone audio
# Grant access to usb
adduser kids_phone plugdev
mkdir -p /usr/bin/kids_phone

# move package to /usr/bin/kids_phone
cp blinker.py cradle.py fetap_keypad.py kids_phone.py /usr/bin/kids_phone/.
chmod +x /usr/bin/kids_phone/kids_phone.py
chown -R kids_phone:kids_phone /usr/bin/kids_phone

# make conf dir and conf file
mkdir -p /etc/kids_phone
cp linphonerc_bak /etc/kids_phone/linphone.conf
chown -R kids_phone:kids_phone /etc/kids_phone

# set uo logging
cp kids_phone_log.conf /etc/rsyslog.d/kids_phone.conf
chmod ag+r /etc/rsyslog.d/kids_phone.conf

# set up service
cp kids_phone.service /etc/systemd/system/kids_phone.service
chmod ag+r /etc/systemd/system/kids_phone.service

