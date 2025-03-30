# from django.db import models
from django.contrib.gis.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from PIL import Image
from gdstorage.storage import GoogleDriveStorage

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
User = get_user_model()

class Mess(models.Model):
    mess_id = models.CharField(max_length = 11, unique = True)
    name = models.CharField(max_length = 30, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='mess', on_delete = models.CASCADE)
    # user = models.EmailField(blank=True, null=True)
    available = models.BooleanField(default = False)
    active = models.BooleanField(default = False)
    r = models.BooleanField(default = False)
    i = models.BooleanField(default = False)
    a = models.BooleanField(default = False)
    d = models.BooleanField(default = False)
    am = models.BooleanField(default = False)
    date_created = models.DateTimeField(null=True, blank=True)
    date_updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Mess'

    def __str__(self):
        return self.mess_id

NO_OF_PERSON = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4')
)
class MessRoom(models.Model):
    mess = models.ForeignKey(Mess, related_name='rooms', on_delete = models.CASCADE)
    persons_per_room = models.CharField(max_length = 1, choices = NO_OF_PERSON)
    expected_rent_per_person = models.DecimalField(max_digits = 64, decimal_places = 2)
    expected_deposit_per_person = models.DecimalField(max_digits = 64, decimal_places = 2)
    cupboard = models.BooleanField(default = False)
    bedding = models.BooleanField(default = False)
    ac = models.BooleanField(default = False)
    tv = models.BooleanField(default = False)
    geyser = models.BooleanField(default = False)
    attached_bathroom = models.BooleanField(default = False)

    def __str__(self):
        return self.mess.mess_id

PIC_TYPE = (
    ('Kitchen', 'Kitchen'),
    ('Bedroom', 'Bedroom'),
    ('Dining', 'Dining'),
    ('Drawing', 'Drawing'),
    ('Hall', 'Hall'),
    ('Bathroom', 'Bathroom'),
    ('Balcony', 'Balcony'),
    ('Outside', 'Outside'),
    ('Other', 'Other')
)
class MessImage(models.Model):
    mess = models.ForeignKey(Mess, related_name='images', on_delete=models.CASCADE)
    image_id = models.CharField(max_length = 10, unique = True)
    image = models.ImageField(upload_to = 'mess', storage=gd_storage)
    type = models.CharField(max_length = 20, choices=PIC_TYPE, blank=True, null=True)

    def __str__(self):
        return self.image_id

    def image_tag(self):
        return format_html('<img src="{}" width="150" height="150" />'.format(self.image.url))
    image_tag.short_description = 'Image'

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     img = Image.open(self.image)
    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save()

class MessAddress(models.Model):
    mess = models.OneToOneField(Mess, related_name='address', on_delete = models.CASCADE)
    # lat = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    # lon = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    street = models.CharField(max_length = 50)
    landmark = models.CharField(max_length = 100, blank=True, null=True)
    area = models.CharField(max_length = 50)
    city = models.CharField(max_length = 50, blank=True, null=True)
    state = models.CharField(max_length = 60)
    zip_code = models.CharField(max_length = 10)
    location = models.PointField(blank=True, null=True)
    class Meta:
        verbose_name_plural = 'Mess Address'

    def __str__(self):
        return self.mess.mess_id

AVAILABLE_FOR = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('A', 'Anyone')
)
PREFERED_GUEST = (
    ('W', 'Working Proffesional'),
    ('S', 'Student'),
    ('B', 'Both')
)
class MessDetails(models.Model):
    mess = models.OneToOneField(Mess, related_name='details', on_delete = models.CASCADE)
    #details about ur place
    place_available_for = models.CharField(max_length = 1, choices = AVAILABLE_FOR)
    prefferable_guest = models.CharField(max_length = 1, choices = PREFERED_GUEST)
    available_from = models.DateField()
    food_included = models.BooleanField(default=False)
        #rules
    no_smoking = models.BooleanField(default = False)
    no_guardians_stay = models.BooleanField(default = False)
    no_drinking = models.BooleanField(default = False)
    no_girl_entry = models.BooleanField(default = False)
    no_boys_entry = models.BooleanField(default = False)
    no_non_veg = models.BooleanField(default = False)
    gate_closing_time = models.TimeField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Mess Details'

    def __str__(self):
        return self.mess.mess_id

class MessAmenities(models.Model):
    mess = models.OneToOneField(Mess, related_name='amenities', on_delete = models.CASCADE)
    #Amenities
    laundry = models.BooleanField(default = False)
    room_cleaning = models.BooleanField(default = False)
    warden_facility = models.BooleanField(default = False)

        #available amenites
    #common_TV = models.BooleanField(default = False)
    #mess = models.BooleanField(default = False)
    #refrigerator = models.BooleanField(default = False)
    lift = models.BooleanField(default = False)
    wifi = models.BooleanField(default = False)
    cooking_allow = models.BooleanField(default = False)
    power_backup = models.BooleanField(default = False)

    parking_for_cycle = models.BooleanField(default = False)
    parking_for_motor_bike = models.BooleanField(default = False)
    parking_for_car = models.BooleanField(default = False)

    class Meta:
        verbose_name_plural = 'Mess Amenities'

    def __str__(self):
        return self.mess.mess_id

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    request = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.phone_number)

class MessInWishlist(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='wishlist')
    mess = models.ForeignKey(Mess, on_delete=models.CASCADE, related_name='mess')
    room_type = models.CharField(blank=True, null=True, max_length=1, choices=NO_OF_PERSON)
    booked = models.BooleanField(default = False)
    booking_complete = models.BooleanField(default = False)

    def __str__(self):
        return self.mess.mess_id
