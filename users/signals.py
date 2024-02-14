from django.dispatch import receiver
from .models import *
from django.db.models.signals import post_save, pre_save
# from web_socket.models import *
from transactions.models import UserServiceMode
from locations.models import UserLocation
from analytics.models import UserRating


@receiver(post_save, sender=User)
def create_instance(sender, instance, created, **kwargs):
    if created:
        try:
            # user infos
            UserInformation.objects.create(
                user=instance
            )
            UserNidInformation.objects.create(
                user=instance
            )
            # user service
            UserServiceMode.objects.create(
                user=instance
            )
            # location
            UserLocation.objects.create(
                user=instance.id,
                user_phone_number=instance.phone_number,
            )
            # analytics rating
            UserRating.objects.create(
                user=instance
            )
        except:
            pass
