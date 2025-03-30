from django.contrib.gis.db import models
from django.conf import settings
from gdstorage.storage import GoogleDriveStorage
from django.contrib.auth import get_user_model

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

gd_storage = GDStorage() #GoogleDriveStorage()
User = get_user_model()

class Hotel(models.Model):
    hotel_id = models.CharField(max_length = 15, unique = True)
    slug = models.SlugField(max_length=200)
    name = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                related_name='hotel', 
                                on_delete=models.CASCADE
                                )
    available = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    date_created = models.DateTimeField(null=True, blank=True)
    date_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.hotel_id

class HotelAddress(models.Model):
    hotel = models.OneToOneField(Hotel, related_name='address', on_delete=models.CASCADE)
    lat = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    lon = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)    
    street = models.CharField(max_length = 50)
    landmark = models.CharField(max_length = 100, blank=True, null=True)
    area = models.CharField(max_length = 50)
    city = models.CharField(max_length = 50, blank=True, null=True)
    state = models.CharField(max_length = 60)
    zip_code = models.CharField(max_length = 10)
    location = models.PointField(blank=True, null=True)
    class Meta:
        verbose_name_plural = 'Hotel Address'

    def __str__(self):
        return self.mess.mess_id

class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='images', on_delete=models.CASCADE)
    image_id = models.CharField(max_length = 10, unique = True)
    image = models.ImageField(upload_to = 'mess', storage=gd_storage)

    def __str__(self):
        return self.image_id