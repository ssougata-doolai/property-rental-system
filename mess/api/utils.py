import string
import random
from mess.models import Mess, MessImage

def mess_id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    the_id =  "".join(random.choice(chars) for x in range(size))
    try:
        Mess.objects.get(mess_id = the_id)
        id_generator()
    except Mess.DoesNotExist:
        return "Mess_" + the_id

def image_id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    the_id =  "".join(random.choice(chars) for x in range(size))
    try:
        MessImage.objects.get(image_id = the_id)
        id_generator()
    except MessImage.DoesNotExist:
        return "Img_" + the_id
