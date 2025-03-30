from django.contrib import admin
from .models import (
    Hotel, 
    HotelAddress,
    HotelImage
)

admin.site.register(Hotel)
admin.site.register(HotelAddress)
admin.site.register(HotelImage)

