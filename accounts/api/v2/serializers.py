from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .utils import PhoneNumberField
from rest_framework.fields import CurrentUserDefault
from django.contrib.auth import authenticate
from accounts.models import Profile, UserEmail
from django.contrib.auth import authenticate, user_logged_in
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate, login
import random
import string
User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['phone_number'] = str(user.phone_number)
        return token

def check_phone(phone):
    try:
        obj = User.objects.get(phone_number=phone)
    except User.DoesNotExist:
        raise ValidationError(
            _('No user found')
        )

class VerifyPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone_number', ]

class ForgotVerifyPhoneSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(validators=[check_phone])

otp_regex = RegexValidator(regex = r'^\+?1?\d{6,6}$', message = "Enter a valid otp")
class PhoneOtpSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    otp = serializers.CharField(max_length=6, validators=[otp_regex])

class SetPasswordSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    password = serializers.CharField(style={'input': 'password'}, write_only=True)
    confirm_password = serializers.CharField(style={'input': 'password'}, write_only=True)

    def save(self):
        phone_number = self.validated_data['phone_number']
        try:
            user = User.objects.get(phone_number = phone_number)
        except User.DoesNotExist:
            user = User(phone_number = phone_number)
        password = self.validated_data['password']
        password2 = self.validated_data['confirm_password']

        if len(password) > 7:
            if password != password2:
                raise serializers.ValidationError({'password': 'Password and Confirm password did not match'})
        else:
            raise serializers.ValidationError({'password': 'Password must have atleast 8 characters !'})
        user.set_password(password)
        user.save()
        return user

class ChangePasswordSerilizer(serializers.Serializer):
    # email = serializers.EmailField()
    current_password = serializers.CharField(style={'input': 'password'}, write_only=True)
    new_password = serializers.CharField(style={'input': 'password'}, write_only=True)
    confirm_new_password = serializers.CharField(style={'input': 'password'}, write_only=True)

    def save(self):
        user =  self.context['request'].user
        password = self.validated_data['current_password']
        user = authenticate(phone_number=user.phone_number, password=password)
        if user is not None:
            password1 = self.validated_data['new_password']
            password2 = self.validated_data['confirm_new_password']
            if len(password1) > 7:
                if password == password1:
                    raise serializers.ValidationError({'new password': 'Current password and new password can not be same'})
                if password1 != password2:
                    raise serializers.ValidationError({'new password': 'New password and new confirm password did not match'})
            else:
                raise serializers.ValidationError({'new password': 'New password must have atleast 8 characters !'})
            user.set_password(password1)
        else:
            raise serializers.ValidationError({'password': 'Invalid password'})
        user.save()
        return user

def check_email(email):
    try:
        obj = UserEmail.objects.get(email=email, validated=True)
        raise ValidationError(
            _('Email already used.')
        )
    except UserEmail.DoesNotExist:
        pass

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[check_email])

otp_regex = RegexValidator(regex = r'^\+?1?\d{6,6}$', message = "Enter a valid otp")
class EmailOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

# class UserEmailSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(required=False)
#     class Meta:
#         model = UserEmail
#         fields = ['email', ]

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    email = serializers.EmailField(required=False)
    class Meta:
        model = Profile
        # fields = ['user', 'profile_id', 'name', 'email', 'profile_pic', 'dob']
        exclude = ['id', ]
        extra_kwargs = {
            'user': {'read_only': True},
            'profile_id': {'read_only': True}
        }
    def update(self, instance, validated_data):
        email = validated_data.get('email')
        if email is not None:
            try:
                obj = instance.email
                if obj.email != email:
                    obj.email = email
                    obj.validated = False
                    obj.subscribed = False
                    obj.save()
            except UserEmail.DoesNotExist:
                obj = UserEmail.objects.create(profile=instance, email=email)
        instance.name = validated_data.get('name', instance.name)
        loc = 'media'
        print(instance.profile_pic.storage.listdir(loc))
        print(instance.profile_pic.storage.listfile())
        try:
            instance.profile_pic = validated_data.get('profile_pic')
            name = instance.profile_pic.name
            while instance.profile_pic.storage.exists(name):
                print(name)
                output_string = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(6))
                name = name.split('.')[0]+output_string+'.'+name.split('.')[1]
            instance.profile_pic.name = name
            print(instance.profile_pic.name)
        except Exception as e:
            print(e)
        instance.dob = validated_data.get('dob', instance.dob)
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.save()
        return instance
