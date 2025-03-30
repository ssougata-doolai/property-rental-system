from rest_framework import status
from rest_framework.response import Response
from accounts.api.v2.serializers import (
        VerifyPhoneSerializer,
        ForgotVerifyPhoneSerializer,
        PhoneOtpSerializer,
        SetPasswordSerializer,
        ChangePasswordSerilizer,
        ProfileSerializer,
        VerifyEmailSerializer,
        EmailOtpSerializer
    )
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.utils import timezone
from accounts.models import PhoneOTP, Profile, UserEmail
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from axes.decorators import axes_dispatch
from django.utils.decorators import method_decorator

import random

from .utils import (
    cal_phone_time,
    send_phone_otp,
    cal_email_time,
    send_email_otp
    )


@method_decorator(axes_dispatch, name='dispatch')
class ObtainTokenPairWithPhoneView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

class VerifyPhoneView(APIView):
    def post(self, request):
        try:
            flag = request.data['flag']
            flag = int(flag)
            if flag != 1 and flag != 2:
                return Response({'flag': ['Invalid flag value.']})
        except:
            return Response({'flag': ['This field is required.']})
        if flag == 1:
            serializer = VerifyPhoneSerializer(data = request.data)
        else:
            serializer = ForgotVerifyPhoneSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        data = send_phone_otp(phone_number)
        if data is not None:
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data)

class VerifyPhoneOtpView(APIView):
    def post(self, request):
        serializer = PhoneOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        t3, obj = cal_phone_time(phone_number)
        if t3 is None:
            return Response({'response': 'Please check your phone number no'}, status=status.HTTP_400_BAD_REQUEST)
        if(t3.seconds > 600):
            data = {
                'response': 'Session has expaired. Please resend otp.'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        otp = serializer.validated_data['otp']
        if obj.validate == True:
            return Response({'response': 'Otp already matched. Please continue...'}, status=status.HTTP_400_BAD_REQUEST)
        if otp == obj.otp:
            obj.validate = True
            obj.validated_time = timezone.now()
            obj.save()
            return Response({'response': 'Otp matched. Create your account'})
        else:
            return Response({'response':'Wrong otp'}, status=status.HTTP_400_BAD_REQUEST)

class SetPasswordView(APIView):
    def post(self, request):
        user = SetPasswordSerializer(data = request.data)
        user.is_valid(raise_exception=True)
        phone_number = user.validated_data['phone_number']
        t3, obj = cal_phone_time(phone_number)
        if t3 is None:
            return Response({'response': 'Please first verify your phone number'}, status=status.HTTP_400_BAD_REQUEST)
        t1 = timezone.now()
        t2 = obj.validated_time
        t3 = t1 - t2
        if(t3.seconds > 600):
            data = {
                'response': 'Session has expaired. Please Verify your phone number again.'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if obj.validate == False:
            return Response({'response': 'First verify OTP'}, status=status.HTTP_400_BAD_REQUEST)
        user.save()
        obj = PhoneOTP.objects.get(phone_number = phone_number)
        obj.delete()
        return Response(user.data)

class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = ChangePasswordSerilizer(data = request.data, context={'request': request})
        user.is_valid(raise_exception = True)
        user.save()
        statu = {
            'phone_number': str(request.user.phone_number),
            'response': 'Password changed successfully'
        }
        return JsonResponse(statu)

class EditProfileView(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class VerifyEmailView(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            obj = UserEmail.objects.get(profile=request.user.profile)
            if obj.email != email:
                obj.email = email
                obj.validated = False
                obj.subscribed = False
                obj.save()
        except UserEmail.DoesNotExist:
            UserEmail.objects.create(profile=request.user.profile, email=email)
        data = send_email_otp(email)
        if data is not None:
            return Response(data)
        return Response(serializer.data)

class VerifyEmailOtpView(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = EmailOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        t3, obj = cal_email_time(email)
        if t3 is None:
            return Response({'response': 'Please check your email id.'}, status=status.HTTP_400_BAD_REQUEST)
        if(t3.seconds > 600):
            data = {
                'response': 'Session has expaired. Please resend otp.'
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        otp = serializer.validated_data['otp']
        if obj.validate == True:
            return Response({'response': 'Email already verified'}, status=status.HTTP_400_BAD_REQUEST)
        if otp == obj.otp:
            obj.validate = True
            obj.validated_time = timezone.now()
            request.user.profile.email.validated = True
            request.user.profile.email.subscribed = True
            request.user.profile.email.save()
            obj.delete()
            return Response({'response': 'Email verified'})
        else:
            return Response({'response':'Wrong otp'}, status=status.HTTP_400_BAD_REQUEST)
