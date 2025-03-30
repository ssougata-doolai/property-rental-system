from rest_framework import status, serializers, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from hotel.api.v1.utils import hotel_id_generator, image_id_generator
from hotel.models import (
    Hotel,
    HotelAddress,
    HotelImage
)

from .serializers import (
    HotelSerializer,
    HotelAddressSerializer,
    HotelImageSerializer
)

User = get_user_model()

def get_hotel(hotel_id, user=None):
    if user is None:
        try:
            hotel = Hotel.objects.get(hotel_id=hotel_id)
        except Hotel.DoesNotExist:
            raise serializers.ValidationError({'response': '404 not found'})
    else:
        try:
            hotel = Hotel.objects.get(hotel_id=hotel_id, user=user)
        except:
            raise serializers.ValidationError({'response': 'Access Forbidden!'})    
    return hotel 

class CreateHotel(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def post(self, request):
        if request.user.hotel.all().count() >= 10:
            return Response({'response': 'You can\'t create more than 5 hotel'})
        hotel = Hotel()
        hotel.hotel_id = hotel_id_generator()
        hotel.user = request.user
        hotel.save()
        data = {
            'id': hotel.hotel_id
        }
        return Response(data)

class CreateHotelImage(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def get(self, request, hotel_id, img_id=None):
        hotel = get_hotel(hotel_id, request.user)
        images = hotel.images.all()
        serialize = HotelImageSerializer(images, many=True)
        return Response(serialize.data)
    
    def post(self, request, hotel_id, img_id=None):
        hotel = get_hotel(hotel_id, request.user)
        if img_id in None:
            if hotel.images.count() <= 10:
                image = MessImageSerializer(data=request.data)
                response = "Image uploaded successfully"
            else: 
                return Response({'response': 'Cant upload more than 10 pics'})
        else:
            try:
                img = hotel.images.get(image_id=img_id)
                image = HotelImageSerializer(img, data=request.data, partial=True)
                response = "Image updated succesfully"
            except HotelImage.DoesNotExist:
                return Response({'response': 'Image not found'})
        image.is_valid(raise_exception=True)
        if hotel.available == True:
            hotel.available = False
            hotel.active = False
            mess.save()
        if img_id is None:
            image.save(hotel=hotel, image_id=image_id_generator())
        else:
            image.save(hotel=hotel)
        if hotel.i == False:
            hotel.save()
        result = image.data 
        data = {
            'id': hotel.hotel_id,
            'response': response,
            'result': result
        }
        return Response(data)
    
    def delete(self, request, hotel_id, img_id):
        hotel = get_hotel(hotel_id, request.user)
        try:
            img = hotel.images.get(image_id=img_id)
            img.delete()
            response = "Image deleted successfully"
        except:
            response = "Access denied or not found"
        return Response({'response': response})