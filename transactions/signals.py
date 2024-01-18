from django.dispatch import receiver
from .models import *
from django.db.models.signals import post_save, pre_save
# from web_socket.models import *
from .models import Transaction
from web_socket.models import SocketRoom

# created several times as it updates
@receiver(post_save, sender=TransactionRequest)
def create_instance(sender, instance, created, **kwargs):
    # if created:
    try:
        # SocketRoom.objects.create(
        #     name = "default",
        #     seeker = instance.seeker,
        #     provider = instance.provider
        # )
        if instance.status == "ACCEPTED" and instance.provider is not None:
            Transaction.objects.create(
                total_amount=instance.amount,
                preferred_notes=instance.preferred_notes,
                provider=instance.provider,
                seeker=instance.seeker,
                charge=(instance.amount * 0.001)
            )

    except:
        pass
