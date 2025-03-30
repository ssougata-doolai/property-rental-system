import string
import random
from .models import Profile

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    the_id =  "".join(random.choice(chars) for x in range(size))
    try:
        Profile.objects.get(profile_id = the_id)
        id_generator()
    except Profile.DoesNotExist:
        return "User_" + the_id
