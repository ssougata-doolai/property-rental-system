from rest_framework import status
from rest_framework.response import Response
from crud.models import Post
from accounts.api.serializers import (
        RegistrationSerializer,
        ChangePasswordSerilizer,
        VerifyEmailSerializer,
        OtpSerializer,
        ForgotVerifyEmailSerializer
    )
import coreapi
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView
from django.http import JsonResponse
from django.utils import timezone
from accounts.models import EmailOTP
import random

class RegistrationSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() in ['post']:
            extra_fields = [
                coreapi.Field(
                    name = 'email',
                    required = True,
                    description='Email Field',
                ),
                coreapi.Field(
                    name = 'password',
                    required = True,
                    description='Password'
                ),
                coreapi.Field(
                    name = 'confirm_password',
                    required = True,
                    description='Confirm Password'
                ),
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields

class ChangePasswordSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() in ['post']:
            extra_fields = [
                coreapi.Field(
                    name = 'email',
                    required = True,
                    description='Email Field',
                ),
                coreapi.Field(
                    name = 'current_password',
                    required = True,
                    description='Password'
                ),
                coreapi.Field(
                    name = 'new_password',
                    required = True,
                    description='Password'
                ),
                coreapi.Field(
                    name = 'confirm_new_password',
                    required = True,
                    description='Confirm Password'
                ),
            ]
        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields

class RegistrationView(APIView):
    def post(self, request):
        user = RegistrationSerializer(data = request.data)
        if user.is_valid():
            user.save()
            return Response(user.data, status=status.HTTP_201_CREATED)
        else:
            return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):

    def post(self, request):
        user = ChangePasswordSerilizer(data = request.data)
        user.is_valid(raise_exception = True)
        user.save()
        statu = {
            'email': user.data['email'],
            'response': 'Password changed successfully'
        }
        return JsonResponse(statu)

def cal_time(email):
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

def send_otp(email):
    otp = random.randint(99999,999999)
    try:
        t3, obj = cal_time(email)
        if t3 is None:
            raise EmailOTP.DoesNotExist
        if(t3.seconds < 6):
            data = {
                'msg': 'please try after 10 sec'
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
    return None

class VerifyEmailView(APIView):
    def post(self, request):
        try:
            flag = request.data['flag']
            flag = int(flag)
            if flag != 1 and flag != 2:
                return Response({'flag': ['Invalid flag value.']})
        except:
            return Response({'flag': ['This field is required.']})
        if flag == 1:
            serializer = VerifyEmailSerializer(data = request.data)
        else:
            serializer = ForgotVerifyEmailSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        data = send_otp(email)
        if data is not None:
            return Response(data)
        return Response(serializer.data)

class VerifyOtpView(APIView):
    def post(self, request):
        serializer = OtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        t3, obj = cal_time(email)
        if t3 is None:
            return Response({'response': 'Please check your email id.'})
        if(t3.seconds > 60):
            data = {
                'response': 'Session has expaired. Please resend otp.'
            }
            return Response(data)
        otp = serializer.validated_data['otp']
        if otp == obj.otp:
            obj.validate = True
            obj.validated_time = timezone.now()
            obj.save()
            return Response({'response': 'Otp matched. Create your account'})
        else:
            return Response({'response':'Wrong otp'})

class SetPasswordView(APIView):
    def post(self, request):
        user = RegistrationSerializer(data = request.data)
        user.is_valid(raise_exception=True)
        email = user.validated_data['email']
        t3, obj = cal_time(email)
        if t3 is None:
            return Response({'response': 'Please first verify your email'})
        t1 = timezone.now()
        t2 = obj.validated_time
        t3 = t1 - t2
        if(t3.seconds > 60):
            data = {
                'response': 'Session has expaired. Please Verify your email again.'
            }
            return Response(data)
        if obj.validate == False:
            return Response({'response': 'First verify OTP'})
        user.save()
        obj = EmailOTP.objects.get(email = email)
        obj.delete()
        return Response(user.data)
