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
sudo apt-get install gunicorn3
```

## Access point for initial setup

See [SETTING UP A RASPBERRY PI AS AN ACCESS POINT IN A STANDALONE NETWORK (NAT)](https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md)
```
sudo apt-get install dnsmasq hostapdsudo
```

## Make kids phone a daemon

See https://www.thomaschristlieb.de/ein-python-script-mit-systemd-als-daemon-systemd-tut-garnicht-weh/

```
sudo ./install.sh
```
