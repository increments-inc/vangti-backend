from django.dispatch import receiver
from .models import *
from django.db.models.signals import post_save, pre_save
# from web_socket.models import *
from .models import Transaction


# created several times as it updates
# @receiver(post_save, sender=TransactionRequest)
# def create_instance(sender, instance, created, **kwargs):
#     # if created:
#     try:
#         if instance.status == "ACCEPTED" and instance.provider is not None:
#             Transaction.objects.create(
#                 total_amount=instance.amount,
#                 preferred_notes=instance.preferred_notes,
#                 provider=instance.provider,
#                 seeker=instance.seeker,
#                 charge=(instance.amount * 0.001)
#             )
#     except:
#         pass

@receiver(post_save, sender=Transaction)
def create_instance(sender, instance, created, **kwargs):
    try:
        if instance.is_completed:
            # transaction history
            try:
                TransactionHistory.objects.get(
                    transaction=instance,
                    provider=instance.provider,
                    seeker=instance.seeker
                )
            except TransactionHistory.DoesNotExist:
                TransactionHistory.objects.create(
                    transaction=instance,
                    total_amount=instance.total_amount,
                    preferred_notes=instance.preferred_notes,
                    provider=instance.provider,
                    seeker=instance.seeker,
                    charge=instance.charge
                )
            # digital wallet
            try:
                DigitalWallet.objects.get(
                    transaction=instance,
                    user=instance.provider
                )
            except DigitalWallet.DoesNotExist:
                DigitalWallet.objects.create(
                    transaction=instance,
                    user=instance.provider,
                    charge=instance.charge,
                    amount=instance.total_amount
                )
    except:
        pass
