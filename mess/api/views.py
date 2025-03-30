from rest_framework import status, serializers, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from mess.api.utils import mess_id_generator, image_id_generator
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .filters import MessFilter
from django.http import JsonResponse
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.geoip2 import GeoIP2
from django.utils import timezone
from mess.models import (
    Mess,
    MessRoom,
    MessAddress,
    MessDetails,
    MessImage,
    MessAmenities,
    Wishlist,
    MessInWishlist
)
from .serializers import (
    MessSerializer,
    MessRoomSerializer,
    MessAddressSerializer,
    MessDetailsSerializer,
    MessImageSerializer,
    MessAmenitiesSerializer,
    MessFilterSerializer,
    MessWishlistFormSerializer
)

User = get_user_model()

def get_mess(mess_id, user=None):
    if user is None:
        try:
            mess = Mess.objects.get(mess_id = mess_id)
        except Mess.DoesNotExist:
            raise serializers.ValidationError({'response':'404 Not Found'})
    else:
        try:
            mess = Mess.objects.get(mess_id = mess_id, user=user)
        except:
            raise serializers.ValidationError({'response': 'Access Forbidden!'})
    return mess

class CreateMess(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def post(self, request):
        if request.user.mess.all().count() >= 10:
            return Response({'response': 'You can\'t create more than 5 mess'})
        mess = Mess()
        mess.mess_id = mess_id_generator()
        mess.user = request.user
        mess.save()
        data = {
            'id': mess.mess_id
        }
        return Response(data)

class GetMess(APIView):
    def get(self, request, mess_id):
        try:
            mess = Mess.objects.get(mess_id=mess_id)
            if mess.active == False or mess.available == False:
                if request.user != mess.user:
                    return Response({'response': 'This mess is not available now'})
        except:
            return Response({'response': '404 not found'})
        serializer = MessSerializer(instance=mess, context={'request': request})
        return Response(serializer.data)

class FilterMessView(generics.ListAPIView):
    queryset = Mess.objects.filter(available=True, active=True)
    serializer_class = MessSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MessFilter

class UserMessListView(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def get(self, request, type):
        paginator = PageNumberPagination()
        paginator.page_size = 10
        if type == 1:
            mess = Mess.objects.filter(user=request.user)
        elif type == 2:
            mess = Mess.objects.filter(user=request.user, available=False)
        elif type == 3:
            mess = Mess.objects.filter(user=request.user, available=True, active=False)
        elif type == 4:
            mess = Mess.objects.filter(user=request.user, available=True, active=True)
        else:
            return Response({'response': 'Invalid type'})
        result_page = paginator.paginate_queryset(mess, request)
        m = MessSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(m.data)

@api_view(['GET', ])
def filter_mess(request):
    paginator = PageNumberPagination()
    paginator.page_size = 2
    result_page = paginator.paginate_queryset(mess, request)
    m = MessSerializer(result_page, many=True, context={'request': request})
    return paginator.get_paginated_response(m.data)

class PublishMess(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def post(self, request, mess_id):
        mess = get_mess(mess_id, request.user)
        if mess.available == True:
            mess.available = False
            mess.save()
            response = 'Mess with id '+mess.mess_id+' is deactivated now and it will not be visible to others'
            return Response({'response': response})
        if mess.r == False:
            return Response({'response': 'Please fill room details form'})
        if mess.i == False:
            return Response({'response': 'Please upload atleast 1 image'})
        if mess.a == False:
            return Response({'response': 'Please set address of mess'})
        if mess.d == False:
            return Response({'response': 'Please fill up the details page of mess'})
        if mess.am == False:
            return Response({'response': 'Please set the amenites of mess'})
        mess.available = True
        if mess.date_created:
            mess.date_updated = timezone.now()
        else:
            mess.date_created = timezone.now()
        mess.save()
        response = 'Mess with id '+mess.mess_id+' is submitted for verification'
        return Response({'response': response})

class DeleteMess(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def delete(self, request, mess_id):
        mess = get_mess(mess_id, request.user)
        mess.delete()
        return Response({'response': 'Deletion successful'})

class MessList(generics.ListAPIView):
    paginate_by = 5
    serializer_class = MessSerializer
    def get_serializer_context(self):
        context = super(MessList, self).get_serializer_context()
        context.update({
            "request": self.request
        })
        return context

    def get_queryset(self):
        mess = Mess.objects.filter(active=True, available=True)
        serializer = MessFilterSerializer(data=self.request.GET)
        serializer.is_valid(raise_exception=True)
        try:
            lat = serializer.validated_data['lat']
            lon = serializer.validated_data['lon']
            print(Point(lat, lon, srid=4326))
            a = mess.filter(
                    address__location__dwithin=(Point(lat, lon, srid=4326), 0.02)
                ).annotate(
                    distance=Distance('address__location', Point(lat, lon, srid=4326))
                ).order_by('distance')
            # a = mess.filter(address__location__distance_lte=(Point(lat, lon, srid=4326), D(m=2000))).annotate(
            #         distance=Distance('address__location', Point(lat, lon, srid=4326))
            #     ).order_by('distance')
            if a.exists():
                mess = a
        except:
            pass
        name = serializer.validated_data.get('name', None)
        if name:
            mess = mess.filter(name__icontains=name)
        try:
            area = serializer.validated_data['area']
            mess = mess.filter(Q(address__area__icontains=area)|Q(address__city__icontains=area)|Q(address__state__icontains=area)|Q(address__zip_code__iexact=area)).distinct()
        except:
            # g = GeoIP2()
            # ip = request.META.get('REMOTE_ADDR', None)
            # print(ip)
            # if ip:
            #     area = g.city(ip)['city']
            # else:
            #     area = 'kolkata'
            # mess = mess.filter(Q(address__area__icontains=area)|Q(address__city__icontains=area)|Q(address__state__icontains=area))
            pass
        available_for = serializer.validated_data.get('place_available_for', None)
        if available_for:
            mess = mess.filter(details__place_available_for__iexact=available_for)
        persons_per_room = serializer.validated_data.get('persons_per_room', None)
        if persons_per_room:
            mess = mess.filter(rooms__persons_per_room__iexact=persons_per_room)
        guest = serializer.validated_data.get('prefferable_guest', None)
        if guest:
            mess = mess.filter(details__prefferable_guest__iexact=guest)
        max_price = serializer.validated_data.get('max_price', None)
        if max_price:
            mess = mess.filter(rooms__expected_rent_per_person__lte=max_price).distinct()
        min_price = serializer.validated_data.get('min_price', None)
        if min_price:
            mess = mess.filter(rooms__expected_rent_per_person__gte=min_price).distinct()
        zip = serializer.validated_data.get('zip', None)
        if zip:
            mess = mess.filter(address__zip_code__icontains=zip)
        return mess


class MessVisibleList(generics.ListAPIView):
    queryset = Mess.objects.filter(available=True, active=True)
    serializer_class = MessSerializer

class CreateMessRoom(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def get(self, request, mess_id):
        mess = get_mess(mess_id, request.user)
        rooms = mess.rooms.all()
        serialize = MessRoomSerializer(rooms, many = True)
        return Response(serialize.data)

    def post(self, request, mess_id):
        mess = get_mess(mess_id, request.user)
        try:
            p = request.data['persons_per_room']
        except:
            return Response({'persons_per_room': ['This field is required.']})
        try:
            obj = mess.rooms.get(persons_per_room = p)
        except:
            obj = None
        if obj is None:
            room = MessRoomSerializer(data = request.data)
            response = 'Created successfully'
        else:
            room = MessRoomSerializer(obj, data=request.data)
            response = 'Updated successfully'
        room.is_valid(raise_exception=True)
        room.save(mess=mess)
        if mess.r == False:
            mess.r = True
            mess.save()
        data = {
            'id': mess.mess_id,
            'response': response
        }
        return Response(data)

class CreateMessAddress(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def get(self, request, mess_id):
        mess = get_mess(mess_id, request.user)
        try:
            address = mess.address
        except:
            return Response({'response': []})
        serialize = MessAddressSerializer(address)
        return Response(serialize.data)

    def post(self, request, mess_id):
        mess = get_mess(mess_id, request.user)
        try:
            obj = mess.address
        except:
            obj = None
        if obj is None:
            addr = MessAddressSerializer(data = request.data)
            response = 'Created successfully'
        else:
            addr = MessAddressSerializer(obj, data=request.data)
            response = 'Updated successfully'
        addr.is_valid(raise_exception=True)
        if mess.available == True:
            mess.active = False
            mess.available = False
            mess.save()
        try:
            lat = addr.validated_data['lat']
            lon = addr.validated_data['lon']
            location = Point(lat, lon, srid=4326)
        except:
            location = None
        addr.save(mess=mess, location=location)
        if mess.a == False:
            mess.a = True
            mess.save()
        data = {
            'id': mess.mess_id,
            'response': response
        }
        return Response(data)

class CreateMessDetails(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def get(self, request, mess_id):
        mess = get_mess(mess_id, request.user)
        try:
            details = mess.details
        except:
            return Response({'response': 'Not found'})
        serialize = MessDetailsSerializer(details)
        return Response(serialize.data)

    def post(self, request, mess_id):
        mess = get_mess(mess_id, request.user)
        try:
            obj = mess.details
        except:
            obj = None
        if obj is None:
            detail = MessDetailsSerializer(data = request.data)
            response = 'Created successfully'
        else:
            detail = MessDetailsSerializer(obj, data=request.data)
            response = 'Updated successfully'
        detail.is_valid(raise_exception=True)
        detail.save(mess=mess)
        try:
            name = detail.validated_data['name']
            mess.name = name
            mess.save()
        except:
            pass
        if mess.d == False:
            mess.d = True
            mess.save()
        data = {
            'id': mess.mess_id,
            'response': response
        }
        return Response(data)
#
class CreateMessImage(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def get(self, request, mess_id, img_id=None):
        mess = get_mess(mess_id, request.user)
        images = mess.images.all()
        serialize = MessImageSerializer(images, many=True)
        return Response(serialize.data)

    def post(self, request, mess_id, img_id=None):
        mess = get_mess(mess_id, request.user)
        if img_id is None:
            if mess.images.count() <= 10:
                image = MessImageSerializer(data=request.data)
                response = "Created successfully"
            else:
                return Response({'response': 'Can not upload images more than 10'})
        else:
            try:
                img = mess.images.get(image_id=img_id)
                image = MessImageSerializer(img, data=request.data, partial=True)
                response = "Updated successfully"
            except MessImage.DoesNotExist:
                return Response({'response': 'Image not found'})
        image.is_valid(raise_exception=True)
        if mess.available == True:
            mess.available = False
            mess.active = False
            mess.save()
        if img_id is None:
            image.save(mess=mess, image_id=image_id_generator())
        else:
            image.save(mess=mess)
        if mess.i == False:
            mess.i = True
            mess.save()
        result = image.data
        data = {
            'id': mess.mess_id,
            'response': response,
            'result': result
        }
        return Response(data)

    def delete(self, request, mess_id, img_id):
        mess = get_mess(mess_id, request.user)
        try:
            img = mess.images.get(image_id=img_id)
            img.delete()
            response = "Image deleted successfully"
        except:
            response = "Access denied or not found"
        return Response({'response': response})

class CreateMessAmenities(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def get(self, request, mess_id):
        mess = get_mess(mess_id, request.user)
        try:
            address = mess.amenities
        except MessAmenities.DoesNotExist:
            return Response({'response': 'Not found'})
        serialize = MessAmenitiesSerializer(address)
        return Response(serialize.data)

    def post(self, request, mess_id):
        mess = get_mess(mess_id, request.user)
        try:
            obj = mess.amenities
        except MessAmenities.DoesNotExist:
            obj = None
        if obj is None:
            ame = MessAmenitiesSerializer(data = request.data)
            response = 'Created successfully'
        else:
            ame = MessAmenitiesSerializer(obj, data=request.data)
            response = 'Updated successfully'
        ame.is_valid(raise_exception=True)
        ame.save(mess=mess)
        if mess.am == False:
            mess.am = True
            mess.save()
        data = {
            'id': mess.mess_id,
            'response': response
        }
        return Response(data)

class CreateMessWishList(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def get(self, request):
        mess = MessInWishlist.objects.filter(wishlist__user=request.user)
        l = []
        for m in mess:
            l.append({'mess_id': m.mess.mess_id, 'room_type': m.room_type})
        m = MessWishlistFormSerializer(l, many=True)
        return Response(m.data)

    def post(self, request):
        serializer = MessWishlistFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mess_id = serializer.data['mess_id']
        room_type = serializer.data.get('room_type', None)
        booking = serializer.data.get('booking', None)
        mess = get_mess(mess_id)
        if room_type is not None:
            try:
                mess.rooms.get(persons_per_room=room_type)
            except MessRoom.DoesNotExist:
                return Response({'response': 'No such room type found'})
        if mess.available == False or mess.active == False:
            return Response({'response': 'Mess is not available for now'})
        try:
            mess_list = MessInWishlist.objects.get(wishlist__user=request.user, mess=mess, room_type=room_type)
            if booking == True:
                if mess_list.booked == False:
                    mess_list.booked = True
                    mess_list.save()
                    response = "Booking request submitted"
                else:
                    mess_list.delete()
                    response = "Booking request cancled"
            else:
                mess_list.delete()
                response = "Removed from wishlist"
            return Response({'response': response})
        except MessInWishlist.DoesNotExist:
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            if booking == True:
                MessInWishlist.objects.create(wishlist=wishlist, mess=mess, room_type=room_type, booked=True)
                response = "Booking request submitted"
            else:
                MessInWishlist.objects.create(wishlist=wishlist, mess=mess, room_type=room_type)
                response = "Added to wishlist"
            return Response({'response': response})

class RequestForMess(APIView):
    authentication_classes = [JWTAuthentication, ]
    permission_classes = [IsAuthenticated, ]
    def post(self, request):
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        if wishlist.request == True:
            return Response({'response': 'Already requested for getting mess'})
        else:
            wishlist.request = True
            wishlist.save()
            return Response({'response': 'Request submitted. We will contact you soon'})
