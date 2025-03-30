from accounts.models import PhoneOTP, EmailOTP
import random
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from phonenumber_field.phonenumber import to_python
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail

import requests
import json

class PhoneNumberField(serializers.CharField):
    default_error_messages = {"invalid": _("Enter a valid phone number.")}

    def to_internal_value(self, data):
        phone_number = to_python(data)
        if phone_number and not phone_number.is_valid():
            raise ValidationError(self.error_messages["invalid"])
        return phone_number

def send_otp_to_mail(email, otp):
    subject = 'Activate your email'
    message = render_to_string("accounts/activation_message.txt", {'otp': otp})
    send_mail(subject, message, from_mail, [email,], fail_silently=False,)

def cal_email_time(email):
    try:
        obj = EmailOTP.objects.get(email = email)
    except EmailOTP.DoesNotExist:
        return None, None
    t1 = timezone.now()
    t2 = obj.updated_date
    if obj.updated_date:
        t2 = obj.updated_date
    else:
        t2 = obj.created_date
    t3 = t1 - t2
    return t3, obj

def send_email_otp(email):
    otp = random.randint(99999,999999)
    try:
        t3, obj = cal_email_time(email)
        if t3 is None:
            raise EmailOTP.DoesNotExist
        if(t3.seconds < 30):
            data = {
                'msg': 'please try after 30 sec'
            }
            return data
        obj.otp = otp
    except EmailOTP.DoesNotExist:
        obj = EmailOTP.objects.create(email = email, otp=otp)
    obj.count += 1
    obj.validate = False
    obj.save()
    print(obj.otp)
    #send_mail
    #send_otp_to_mail(email, otp)
    return None

def fast_to_sms(phone_number, otp):
    code = '{#BB#}'
    url = "https://www.fast2sms.com/dev/bulk"
    payload = f"sender_id=FSTSMS&language=english&route=qt&numbers={phone_number}&message=35664&variables={code}&variables_values={otp}"
    headers = {
        'authorization': "BpTfKdRx04wPzZhCoblNELv9Dy3gWrJ8tISH2McAX1n6eQVO7kpunhmZKUfogwDqECNWjz2YbyLTPG84",
        'cache-control': "no-cache",
        'content-type': "application/x-www-form-urlencoded"
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)
    return response.text

def cal_phone_time(phone_number):
    try:
        obj = PhoneOTP.objects.get(phone_number = phone_number)
    except PhoneOTP.DoesNotExist:
        return None, None
    t1 = timezone.now()
    t2 = obj.updated_date
    if obj.updated_date:
        t2 = obj.updated_date
    else:
        t2 = obj.created_date
    t3 = t1 - t2
    return t3, obj

def send_phone_otp(phone_number):
    otp = random.randint(99999,999999)
    try:
        t3, obj = cal_phone_time(phone_number)
        if t3 is None:
            raise PhoneOTP.DoesNotExist
        if(t3.seconds < 30):
            data = {
                'msg': 'please try after 30 sec'
            }
            return data
        obj.otp = otp
    except PhoneOTP.DoesNotExist:
        obj = PhoneOTP.objects.create(phone_number = phone_number, otp=otp)
    if obj.count > 5:
        t1 = timezone.now()
        t2 = obj.created_date
        t3 = t1 - t2
        if t3.days < 1:
            return {'response': 'You can\'t send more than 6 otp in a day'}
        else:
            obj.created_date = timezone.now()
            obj.count = 0
    #send_otp_message
    # resp = fast_to_sms(phone_number, otp)
    # print(resp)
    # resp = json.loads(resp)
    # print(resp)
    # if resp['return'] == False:
    #     return {'response': resp['message']}
    obj.count += 1
    obj.validate = False
    obj.save()
    print(obj.otp)
    return None
