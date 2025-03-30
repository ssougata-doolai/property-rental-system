from rest_framework import serializers
from django.contrib.auth import get_user_model
from gdstorage.storage import GoogleDriveStorage
from hotel.models import (
    Hotel,
    HotelAddress,
    HotelImage
)

User = get_user_model()
gd_storage = GoogleDriveStorage()

class HotelAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        exclude = ['id', 'hotel'] 
        extra_kwargs = {
            'image_id': {'required': False}
        }

class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        exclude = ['id', 'hotel'] 
        extra_kwargs = {
            'image_id': {'required': False}
        }

class HotelSerializer(serializers.ModelSerializer):
    pass 
