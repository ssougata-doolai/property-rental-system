from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={'input': 'password'}, write_only=True)
    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        email = self.validated_data['email']
        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            user = User(email = email)
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
    email = serializers.EmailField()
    current_password = serializers.CharField(style={'input': 'password'}, write_only=True)
    new_password = serializers.CharField(style={'input': 'password'}, write_only=True)
    confirm_new_password = serializers.CharField(style={'input': 'password'}, write_only=True)

    def save(self):
        email = self.validated_data['email']
        try:
            User.objects.get(email = email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'User with this email id does not exist!'})
        password = self.validated_data['current_password']
        user = authenticate(email=email, password=password)
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

class VerifyEmailSerializer(serializers.ModelSerializer):
    # flag = serializers.IntegerField(validators=[validate_flag], write_only=True)
    class Meta:
        model = User
        fields = ['email', ]

def check_email(email):
    try:
        obj = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValidationError(
            _('No user found')
        )
class ForgotVerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[check_email])

otp_regex = RegexValidator(regex = r'^\+?1?\d{6,6}$', message = "Enter a valid otp")
class OtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
