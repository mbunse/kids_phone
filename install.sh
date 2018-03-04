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
cp -f blinker.py cradle.py fetap_keypad.py kids_phone.py /usr/bin/kids_phone/.
chmod +x /usr/bin/kids_phone/kids_phone.py
chown -R kids_phone:kids_phone /usr/bin/kids_phone

# make conf dir and conf file
mkdir -p /etc/kids_phone
cp -f linphonerc_bak /etc/kids_phone/linphone.conf
chown -R kids_phone:kids_phone /etc/kids_phone
chmod ag+r /etc/kids_phone/linphone.conf
chmod g+w /etc/kids_phone/linphone.conf

# set up logging
cp -f kids_phone_log.conf /etc/rsyslog.d/kids_phone.conf
chmod ag+r /etc/rsyslog.d/kids_phone.conf

# set up service
cp -f kids_phone.service /etc/systemd/system/kids_phone.service
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

# give rioghts to start and stop kids_phone
mkdir -p /etc/polkit-1/rules.d
cp -f manage-kids_phone.rules /etc/polkit-1/rules.d/manage-kids_phone.rules

# set up nginx
systemctl stop nginx
# extract IP address to be added to certificate
IP=`ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p'`
echo $IP
# Create certificates if they not alread exist
if [ ! -f "/etc/ssl/private/ssl-cert-kids_phone.key" ]
then 
    openssl req -x509 -newkey rsa:4096 -keyout ssl-cert-kids_phone.key -out ssl-cert-kids_phone.pem -nodes -subj "/CN=$IP/C=DE"
    mv ssl-cert-kids_phone.key /etc/ssl/private/ssl-cert-kids_phone.key
    mv ssl-cert-kids_phone.pem /etc/ssl/certs/ssl-cert-kids_phone.pem
fi
# replace server name with IP, so that certificate fits to name
cat nginx.conf | sed "s/server_name  localhost/server_name  $IP/g" >  nginx.conf_ip

mv nginx.conf_ip /etc/nginx/nginx.conf
rm -f /etc/nginx/sites-enabled/*

# reload units
systemctl daemon-reload

# Restart logging service
systemctl restart rsyslog

# enable services
systemctl enable kids_phone
systemctl enable kids_phone_www
systemctl restart kids_phone
systemctl restart kids_phone_www
systemctl restart nginx

