from django.shortcuts import render

from .models import Key_And_Number, Caller_Number_Allowed

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

    context = {
        'key_and_number_list': key_and_number_list,
        'caller_number_allowed_list': caller_number_allowed_list,
    }
    return render(request, 'call_numbers/index.html', context)