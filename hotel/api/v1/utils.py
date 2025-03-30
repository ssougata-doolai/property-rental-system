import string
import random
from hotel.models import Hotel, HotelImage

def hotel_id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    the_id =  "".join(random.choice(chars) for x in range(size))
    try:
        Hotel.objects.get(hotel_id = the_id)
        id_generator()
    except Hotel.DoesNotExist:
        return "Hotel_" + the_id

def image_id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    the_id =  "".join(random.choice(chars) for x in range(size))
    try:
        HotelImage.objects.get(image_id = the_id)
        id_generator()
    except HotelImage.DoesNotExist:
        return "Img_" + the_id
