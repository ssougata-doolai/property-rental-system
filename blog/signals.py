from .models import Blog
from .utils import unique_slug_generator
from django.db.models.signals import pre_save

def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
    	instance.slug = unique_slug_generator(instance)

pre_save.connect(pre_save_receiver, sender = Blog)
