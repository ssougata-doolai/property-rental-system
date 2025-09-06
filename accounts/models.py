# from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import Group, Permission, PermissionsMixin
from gdstorage.storage import GoogleDriveStorage
import random
import string
class GDStorage(GoogleDriveStorage):
    def listfile(self):
        results = self._drive_service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))

gd_storage = GDStorage()#GoogleDriveStorage()

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, is_staff = False, is_active=True, is_admin=False):
        if not phone_number:
            raise ValueError('User must have a phone number')
        if not password:
            raise ValueError('User must have a password')

        user_obj = self.model(
            phone_number = phone_number
        )
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.is_superuser = is_admin
        user_obj.active = is_active
        user_obj.save(using=self._db)
        return user_obj

    def create_stuffuser(self, phone_number, password=None):
        user = self.create_user(
            phone_number,
            password = password,
            is_staff = True
        )
        return user

    def create_superuser(self, phone_number, password=None):
        user = self.create_user(
            phone_number,
            password = password,
            is_staff = True,
            is_admin = True
        )
        return user

class User(AbstractBaseUser, PermissionsMixin):
    phone_number = PhoneNumberField(unique=True)
    # phone_number = models.CharField(validators = [phone_regex], unique=True, max_length = 15)
    #phone_number = PhoneField(blank=False, null=False, unique=True, help_text='Contact phone number')
    first_login = models.BooleanField(default = False)
    active = models.BooleanField(default = True)
    staff = models.BooleanField(default = False)
    timestamp = models.DateTimeField(auto_now_add = True)

    USERNAME_FIELD = 'phone_number'
    REQUEIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.phone_number)

    def get_full_name(self):
        return self.phone_number

    def get_short_name(self):
        return self.phone_number

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.is_superuser

    @property
    def is_active(self):
        return self.active

class PhoneCountryCode(models.Model):
    name = models.CharField(max_length=50)
    dial_code = models.CharField(max_length=6)
    code = models.CharField(max_length=4)

    def __str__(self):
        return self.name

class UserEmail(models.Model):
    profile = models.OneToOneField('Profile', related_name='email', on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True)
    validated = models.BooleanField(default=False)
    subscribed = models.BooleanField(default=False)

    def __str__(self):
        return self.email

phone_regex = RegexValidator(regex = r'^\+?1?\d{10,10}$',
message = "Phone number is not valid.")
USER_TYPE = (
    ('b', 'Buyer'),
    ('s', 'Seller'),
)
class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete = models.CASCADE)
    profile_id = models.CharField(max_length=120, unique =True)
    name = models.CharField(max_length=50, blank=True, null=True)
    # email =  models.ForeignKey(UserEmail, blank=True, null=True, on_delete=models.SET_NULL, related_name='user_email')
    profile_pic =  models.ImageField(default='default.png',upload_to = 'account/', storage=gd_storage)
    dob = models.DateField(blank=True, null=True)
    user_type = models.CharField(max_length = 1, choices = USER_TYPE, blank=True, null=True)

    def __str__(self):
        return str(self.user.phone_number)

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

otp_regex = RegexValidator(regex = r'^\+?1?\d{6,6}$', message = "Enter a valid otp")
class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(validators = [otp_regex], max_length=6)
    count = models.IntegerField(default = 0)
    validate = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    validated_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.email) + ' is sent ' + str(self.otp) + '   Count = ' + str(self.count)

class PhoneOTP(models.Model):
    phone_number = PhoneNumberField(blank=False, null=False, help_text='Contact phone number')
    otp = models.CharField(validators = [otp_regex], max_length=6)
    count = models.IntegerField(default = 0)
    validate = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    validated_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.phone_number) + ' is sent ' + str(self.otp) + '   Count = ' + str(self.count)
