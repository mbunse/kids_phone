#!/bin/bash

systemctl disable kids_phone
systemctl disable kids_phone_www

systemctl stop kids_phone
systemctl stop kids_phone_www
systemctl stop nginx

rm -rf /usr/bin/kids_phone

# remove package from /usr/bin/kids_phone
rm -rf /usr/bin/kids_phone

# remove conf dir and conf file
rm -rf /etc/kids_phone

# remove logging
rm -f /etc/rsyslog.d/kids_phone.conf
rm -f /etc/rsyslog.d/kids_phone_www.conf
# remove service
rm -f /etc/systemd/system/kids_phone.service
rm -f /etc/systemd/system/kids_phone_www.service

## remove kids_phone_conf web interface
rm -rf /var/www

# remove start and stop kids_phone
rm /etc/polkit-1/rules.d/manage-kids_phone.rules

# Remove socket dir
rm -rf /var/run/kids_phone

rm -f /etc/nginx/nginx.conf

# reload units
systemctl daemon-reload

# Restart logging service
systemctl restart rsyslog

# remove dedicated user
userdel kids_phone_www
userdel kids_phone
delgroup kids_phone