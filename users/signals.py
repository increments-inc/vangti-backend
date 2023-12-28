from django.dispatch import receiver
from .models import *
from django.db.models.signals import post_save, pre_save
# from web_socket.models import *
from transactions.models import UserServiceMode


@receiver(post_save, sender=User)
def create_instance(sender, instance, created, **kwargs):
    if created:
        try:
            UserInformation.objects.create(
                user=instance
            )

            UserServiceMode.objects.create(
                user=instance
            )
        except:
            pass

