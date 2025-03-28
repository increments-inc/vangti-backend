from datetime import datetime, timedelta

from django.db.models import Sum, Avg
from django.dispatch import receiver
from .models import *
from django.db.models.signals import post_save, pre_save
# from web_socket.models import *
from .models import Transaction
from analytics.models import Analytics, UserRating, UserSeekerRating
from django.conf import settings
from locations.models import UserLocation
from txn_credits.models import CreditUser, ProviderTxnPlatform


@receiver(post_save, sender=Transaction)
def create_instance(sender, instance, created, **kwargs):
    try:
        if instance.is_completed:
            # transaction history
            try:
                t_history = TransactionHistory.objects.get(
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
                    charge=instance.charge,
                )

    except:
        pass


@receiver(post_save, sender=TransactionHistory)
def create_analytics_instance(sender, instance, created, **kwargs):
    if created:
        # digital wallet
        try:
            DigitalWallet.objects.get(
                transaction=instance.transaction,
                user=instance.provider
            )
        except DigitalWallet.DoesNotExist:
            DigitalWallet.objects.create(
                transaction=instance.transaction,
                user=instance.provider,
                charge=instance.charge,
                amount=instance.total_amount
            )

        # Analytics
        try:
            analyt_data = Analytics.objects.get(
                user=instance.provider,
                created_at__date=datetime.now().date()
            )
            analyt_data.no_of_transaction += 1
            analyt_data.profit += instance.charge
            analyt_data.total_amount_of_transaction += instance.total_amount
            analyt_data.save()
        except Analytics.DoesNotExist:
            Analytics.objects.create(
                user=instance.provider,
                no_of_transaction=1,
                profit=instance.charge,
                total_amount_of_transaction=instance.total_amount
            )

        # ProviderTxnPlatform
        try:
            try:
                prov = CreditUser.objects.using("credits").get(
                    user_uid=instance.provider.id
                )
            except CreditUser.DoesNotExist:
                prov = CreditUser.objects.using("credits").create(
                    user_uid=instance.provider.id
                )
            ProviderTxnPlatform.objects.using("credits").create(
                transaction=instance.transaction.id,
                provider=prov,
                profit=instance.charge,
                platform_fee=(instance.charge * settings.PLATFORM_CHARGE)
            )
        except:
            pass
