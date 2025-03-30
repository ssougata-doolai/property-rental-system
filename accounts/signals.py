from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from .models import Profile
from .utils import id_generator
from django.core.exceptions import ObjectDoesNotExist
from defender import signals

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        #Profile.objects.create(user=instance)
        obj = Profile.objects.create(user=instance)
        obj.profile_id = id_generator()
        obj.save()

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        obj = Profile.objects.create(user=instance)
        obj.profile_id = id_generator()
        obj.save()
    #instance.profile.save()


@receiver(signals.username_block)
def username_blocked(username, **kwargs):
    print("%s was blocked!" % username)

@receiver(signals.ip_block)
def ip_blocked(ip_address, **kwargs):
    print("%s was blocked!" % ip_address)
