from datetime import datetime, timedelta

from django.db.models import Sum, Avg
from django.dispatch import receiver
from .models import *
from django.db.models.signals import post_save, pre_save
# from web_socket.models import *
from .models import Transaction
from analytics.models import Analytics, UserRating, UserSeekerRating
from django.conf import settings


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
            # try:
            #     DigitalWallet.objects.get(
            #         transaction=instance,
            #         user=instance.provider
            #     )
            # except DigitalWallet.DoesNotExist:
            #     DigitalWallet.objects.create(
            #         transaction=instance,
            #         user=instance.provider,
            #         charge=instance.charge,
            #         amount=instance.total_amount
            #     )
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
            analyt_data.profit += settings.PROVIDER_COMMISSION
            analyt_data.total_amount_of_transaction += instance.total_amount
            analyt_data.save()
        except Analytics.DoesNotExist:
            Analytics.objects.create(
                user=instance.provider,
                no_of_transaction=1,
                profit=settings.PROVIDER_COMMISSION,
                total_amount_of_transaction=instance.total_amount
            )
        # User Rating
        try:
            rating_data = UserRating.objects.get(
                user=instance.provider
            )
            rating_data.no_of_transaction += 1
            rating_data.total_amount_of_transaction += instance.total_amount
            rating_data.save()
        except UserRating.DoesNotExist:
            UserRating.objects.create(
                user=instance.provider,
                no_of_transaction=1,
                total_amount_of_transaction=instance.total_amount
            )

        # user as seeker rating
        try:
            rating_data = UserSeekerRating.objects.get(
                user=instance.seeker
            )
            rating_data.no_of_transaction += 1
            rating_data.total_amount_of_transaction += instance.total_amount
            rating_data.save()
        except UserSeekerRating.DoesNotExist:
            UserSeekerRating.objects.create(
                user=instance.provider,
                no_of_transaction=1,
                total_amount_of_transaction=instance.total_amount
            )


@receiver(post_save, sender=TransactionReview)
def update_user_rating(sender, instance, created, **kwargs):
    if created:
        # User Rating
        try:
            rating_data = UserRating.objects.get(
                user=instance.provider
            )
            rating_data.rating += instance.rating
            rating_data.save()
        except UserRating.DoesNotExist:
            UserRating.objects.create(
                user=instance.provider,
                rating=instance.rating
            )


@receiver(post_save, sender=UserTransactionResponse)
def update_user_response(sender, instance, created, **kwargs):
    if instance.response_duration is not None:
        average_response_time = UserTransactionResponse.objects.filter(
            provider=instance.provider
        ).aggregate(
            avg_response_time=Avg("response_duration", default=timedelta(seconds=0))
        )["avg_response_time"]
        print(average_response_time)
        # User Rating
        try:
            rating_data = UserRating.objects.get(
                user=instance.provider
            )
            rating_data.provider_response_time = average_response_time
            rating_data.save()
        except UserRating.DoesNotExist:
            UserRating.objects.create(
                user=instance.provider,
                provider_response_time=average_response_time
            )
