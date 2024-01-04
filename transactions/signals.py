from django.dispatch import receiver
from .models import *
from django.db.models.signals import post_save, pre_save
# from web_socket.models import *
from .models import Transaction
from web_socket.models import SocketRoom


@receiver(post_save, sender=Transaction)
def create_instance(sender, instance, created, **kwargs):
    if created:
        try:
            SocketRoom.objects.create(
                name = "default",
                seeker = instance.seeker,
                provider = instance.provider
            )

        except:
            pass
