from django.shortcuts import render
from django.conf import settings

from .models import Key_And_Number, Caller_Number_Allowed, Global_Settings

# Restart kids_phone if SIP account is updated
from pydbus import SystemBus




# parser for linphone config
import configparser

# Regex for parsing sip realm
import re

# Hashing of sip password
import hashlib

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
def index(request, delete_phonenumber=None):
    key_and_number_list = Key_And_Number.objects.all()
    for key_and_number in key_and_number_list:
        key = key_and_number.pk
        input_key = 'key{key_id}'.format(key_id=key)
        if input_key in request.POST:
            key_and_number.phonenumber = request.POST[input_key]
            key_and_number.save()

    if "delete" in request.POST:
        Caller_Number_Allowed.objects.get(pk=request.POST['delete']).delete()

    if "add_phonenumber" in request.POST:
        new_caller_number_allowed = Caller_Number_Allowed(phonenumber=request.POST['add_phonenumber'])
    try:
        new_caller_number_allowed.save()
    except:
        pass


    
    caller_number_allowed_list = Caller_Number_Allowed.objects.order_by("phonenumber")
    key_and_number_list = Key_And_Number.objects.all()

    # Read linphone conf
    config = configparser.ConfigParser()
    config.read(settings.LINPHONERC)

    sip_username = None
    sip_realm = None
    sip_proxy = None

    # Check if user requested update of SIP account information
    if all (k in request.POST for k in ("sip_username","sip_realm", "sip_proxy", "sip_password")):
        sip_username = request.POST["sip_username"]
        sip_realm = request.POST["sip_realm"]
        sip_proxy = request.POST["sip_proxy"]
        sip_password = request.POST["sip_password"]

        config["auth_info_0"]["username"] = sip_username
        config["auth_info_0"]["ha1"] = hashlib.md5(
            "{username}:{realm}:{password}".format(
                username=sip_username, realm=sip_realm, password=sip_password
                ).encode()
            ).hexdigest()
        config["auth_info_0"]["realm"] = sip_realm
        config["proxy_0"]["reg_proxy"] = "<sip:{proxy}>".format(proxy=sip_proxy)
        config["proxy_0"]["reg_identity"] = "sip:{username}@{realm}".format(username=sip_username, realm=sip_realm)
        with open(settings.LINPHONERC, "w") as f:
            config.write(f)
            # Restart kids_phone
            if settings.DEBUG == False:
                SystemBus().get(".systemd1").RestartUnit("kids_phone.service", "fail")


    if "auth_info_0" in config.sections():
        sip_username = config["auth_info_0"]["username"]
        if "realm" in config["auth_info_0"]:
            sip_realm =  config["auth_info_0"]["realm"]
    if "proxy_0" in config.sections():
        if "reg_proxy" in config["proxy_0"]:
            sip_proxy = re.search("<sip:([^>]*)>", config["proxy_0"]["reg_proxy"]).group(1)
        

    context = {
        'key_and_number_list': key_and_number_list,
        'caller_number_allowed_list': caller_number_allowed_list,
        'sip_username': sip_username,
        'sip_realm': sip_realm,
        'sip_proxy': sip_proxy,
    }
    return render(request, 'call_numbers/index.html', context)