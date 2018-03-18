from django.shortcuts import render
from django.conf import settings

from .models import Key_And_Number, Caller_Number_Allowed, Global_Settings

# Restart kids_phone if SIP account is updated
from pydbus import SystemBus

import os

# communication with kids_phone through socket
from socket_client_server import Sock_Client

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

    sip_username = None
    sip_realm = None
    sip_proxy = None

    # Set up client
    server_address = os.getenv("KIDS_PHONE_SOCKET", './kids_phone_socket')
    client = Sock_Client(server_address)

    # Check if user requested update of SIP account information
    if all (k in request.POST for k in ("sip_username","sip_realm", "sip_proxy", "sip_password")):
        sip_username = request.POST["sip_username"]
        sip_realm = request.POST["sip_realm"]
        sip_proxy = request.POST["sip_proxy"]
        sip_password = request.POST["sip_password"]



        # Construct message
        data = {
            "action": "register",
            "data": {
                "username": sip_username,
                "password": sip_password,
                "realm": sip_realm,
                }
        }

        #Send to server
        client.send(data)

    # TODO: Request auth data from server        
    data = {
        "action": "get_registration",
    }
    registration = client.send(data)
    if registration is not None:
        sip_username =  registration["username"]
        sip_realm = registration["realm"]
        sip_proxy = registration["proxy"]
    context = {
        'key_and_number_list': key_and_number_list,
        'caller_number_allowed_list': caller_number_allowed_list,
        'sip_username': sip_username,
        'sip_realm': sip_realm,
        'sip_proxy': sip_proxy,
    }
    return render(request, 'call_numbers/index.html', context)