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

# set up logging
cp kids_phone_log.conf /etc/rsyslog.d/kids_phone.conf
chmod ag+r /etc/rsyslog.d/kids_phone.conf

# set up service
cp kids_phone.service /etc/systemd/system/kids_phone.service
chmod ag+r /etc/systemd/system/kids_phone.service


# create dedicated user
useradd -r -s /bin/false -g kids_phone kids_phone_www

## kids_phone_conf web interface
sudo mkdir -p /var/www
cp -r kids_phone_conf /var/www/.
chown -R kids_phone_www:kids_phone /var/www/kids_phone_conf

# set up logging
cp kids_phone_www_log.conf /etc/rsyslog.d/kids_phone_www.conf
chmod ag+r /etc/rsyslog.d/kids_phone_www.conf

# set up service
cp kids_phone_www.service /etc/systemd/system/kids_phone_www.service
chmod ag+r /etc/systemd/system/kids_phone_www.service

# reload units
systemctl daemon-reload

# Restart logging service
systemctl restart rsyslog

# enable services
systemctl enable kids_phone
systemctl enable kids_phone_www

