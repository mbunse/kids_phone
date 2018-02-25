# kids_phone
Raspberry Pi project for a SIP or VoIP phone for children.

## Prerequisites

### Software
- linphone
- linphone python wrapper
- python GPIO

### Hardware
- USB audio device with mic and phone plug
- buttons (tbd.)

Install linphone and python wrappers for the raspi:
```
sudo apt-get install linphone-nogtk
wget http://linphone.org/releases/linphone-python-raspberry/linphone4raspberry-3.9.1-cp27-none-any.whl
sudo pip install linphone4raspberry-3.9.1-cp27-none-any.whl
```

To register the linphone client on a SIP service run the linphone command line tool:
```
#> linphonec
linphone> register sip:<username>@<SIP_domain> sip:<SIP_domain> <PASSWORD>
```
This will create an rc file `/home/pi/.linphonerc` which will be used a standard configuration file for __kids_phone__.

## Python GPIO modules
```
sudo apt-get install python-dev
```

## Configuration Webserver
```
sudo apt-get install python3-pip
sudo pip3 install django
sudo apt-get install git
```

## Access point for initial setup

See [SETTING UP A RASPBERRY PI AS AN ACCESS POINT IN A STANDALONE NETWORK (NAT)](https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md)
```
sudo apt-get install dnsmasq hostapdsudo
```

## Make kids phone a daemon

See https://www.thomaschristlieb.de/ein-python-script-mit-systemd-als-daemon-systemd-tut-garnicht-weh/

 *  create dedicated system user ( `-r` ) with no logn shell (`-s /bin/false`)
 *  create a dedicated /usr/bin/kids_phone dir

```
sudo useradd -r -s /bin/false kids_phone
# Add user to gpio group to grand access to /dev/mem
sudo adduser kids_phone gpio
# Grant access to audio
sudo adduser kids_phone audio
# Grant access to usb
sudo adduser kids_phone plugdev
sudo mkdir /usr/bin/kids_phone
```

 *  move package to /usr/bin/kids_phone
```
sudo cp *.py /usr/bin/kids_phone/.
sudo chmod +x /usr/bin/kids_phone/kids_phone.py
sudo chown -R kids_phone:kids_phone /usr/bin/kids_phone
```

 *  make conf dir and conf file
```
sudo mkdir /etc/kids_phone
sudo cp linphonerc_bak /etc/kids_phone/linphone.conf
sudo chown -R kids_phone:kids_phone /etc/kids_phone
```
 *  create daemon config file
 
```
sudo nano /etc/systemd/system/kids_phone.service
```
 
Content:
```
[Unit]
Description=Kids phone daemon
Wants=network-online.target
After=network-online.target syslog.target

[Service]
Type=simple
User=kids_phone
Group=kids_phone
WorkingDirectory=/usr/bin/kids_phone/
ExecStart=/usr/bin/kids_phone/kids_phone.py
SyslogIdentifier=kids_phone
StandardOutput=syslog
StandardError=syslog
Restart=no

[Install]
WantedBy=multi-user.target
```

http://wiki.rsyslog.com/index.php/Filtering_by_program_name
https://stackoverflow.com/questions/37585758/how-to-redirect-output-of-systemd-service-to-a-file
 *  create a file `/etc/rsyslog.d/kids_phone.conf`
 
```
sudo nano /etc/rsyslog.d/kids_phone.conf
```
 
Content
```
if $programname == 'kids_phone' then /var/log/kids_phone.log
if $programname == 'kids_phone' then ~
```
