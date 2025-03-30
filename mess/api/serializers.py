from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from gdstorage.storage import GoogleDriveStorage
User = get_user_model()
from mess.models import (
    Mess,
    MessRoom,
    MessAddress,
    MessDetails,
    MessImage,
    MessAmenities,
    MessInWishlist
)
gd_storage = GoogleDriveStorage()

# class MessCreateSerializer(serializers.ModelSerializer):
#     mess = serializers.SlugRelatedField(slug_field='name')
#     class Meta:
#         model = Mess
#         fields = ['mess', ]

class MessRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessRoom
        exclude = ['id', 'mess']

class MessAddressSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(write_only=True, required=False)
    lon = serializers.FloatField(write_only=True, required=False)
    lat1 = serializers.SerializerMethodField()
    lon1 =serializers.SerializerMethodField()
    class Meta:
        model = MessAddress
        exclude = ['id', 'mess', 'location']

    def save(self, mess, location):
        street = self.validated_data.get('street')
        landmark = self.validated_data.get('landmark')
        area = self.validated_data.get('area')
        city = self.validated_data.get('city')
        state = self.validated_data.get('state')
        zip_code = self.validated_data.get('zip_code')
        try:
            address = MessAddress.objects.get(mess=mess)
            address.mess = mess
            address.street=street
            address.landmark=landmark
            address.area=area
            address.city=city
            address.state=state
            address.zip_code=zip_code
            address.location=location
            address.save()
            return address
        except MessAddress.DoesNotExist:
            return MessAddress.objects.create(mess=mess, street=street, landmark=landmark, area=area, city=city, state=state, zip_code=zip_code, location=location)

    def get_lat1(self, obj):
        try:
            x = str(obj.location).split('(')[1].split(' ')[0]
        except:
            x = None
        return x

    def get_lon1(self, obj):
        try:
            x = str(obj.location).split(' ')[2].split(')')[0]
        except:
            x = None
        return x

    def ckeck_user(self):
        request = self.context.get("request")
        if request:
            return True
        else:
            return False

class MessDetailsSerializer(serializers.ModelSerializer):
    # place_available_for = serializers.CharField(source = 'get_place_available_for_display')
    # prefferable_guest = serializers.CharField(source = 'get_prefferable_guest_display')
    name = serializers.CharField(required=False, write_only=True)
    class Meta:
        model = MessDetails
        exclude = ['id', 'mess']

class MessImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessImage
        exclude = ['id', 'mess']
        extra_kwargs = {
            'image_id': {'required': False}
        }

class MessAmenitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessAmenities
        exclude = ['id', 'mess']

class MessSerializer(serializers.ModelSerializer):
    rooms = MessRoomSerializer(many=True, read_only=True)
    address = MessAddressSerializer(read_only=True)
    details = MessDetailsSerializer(read_only=True)
    images = MessImageSerializer(many=True, read_only=True)
    amenities = MessAmenitiesSerializer(read_only=True)
    wishlist = serializers.SerializerMethodField()

    class Meta:
        model = Mess
        fields = ['mess_id', 'user', 'name', 'available', 'active', 'wishlist', 'date_created', 'date_updated', 'rooms', 'address', 'details', 'images', 'amenities']

    def get_wishlist(self, instance):
        try:
            user = self.context['request'].user
        except:
            user = AnonymousUser
        if user.is_authenticated:
            if MessInWishlist.objects.filter(mess=instance, wishlist__user=user).exists():
                return True
            else:
                return False
        else:
            return False

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
class MessFilterSerializer(serializers.Serializer):
    #location
    lat = serializers.FloatField(required=False)
    lon = serializers.FloatField(required=False)
    min_price = serializers.DecimalField(max_digits = 64, decimal_places = 2, required=False)
    max_price = serializers.DecimalField(max_digits = 64, decimal_places = 2, required=False)
    place_available_for = serializers.ChoiceField(choices = AVAILABLE_FOR, required=False)
    prefferable_guest = serializers.ChoiceField(choices = PREFERED_GUEST, required=False)
    persons_per_room = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    area = serializers.CharField(required=False)
    zip = serializers.CharField(required=False)

NO_OF_PERSON = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4')
)
class MessWishlistFormSerializer(serializers.Serializer):
    mess_id = serializers.CharField(max_length=11)
    area = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    room_type = serializers.ChoiceField(choices=NO_OF_PERSON, required=False)
    booking = serializers.BooleanField(required = False)

    def get_images(self, instance):
        mess_id = instance['mess_id']
        serializer = MessImageSerializer(MessImage.objects.filter(mess__mess_id=mess_id), many=True)
        return serializer.data

    def get_area(self, instance):
        mess_id = instance['mess_id']
        obj = MessAddress.objects.get(mess__mess_id=mess_id)
        return obj.area
