from transactions.models import CancelledTransaction, TransactionHistory
from analytics.models import UserRating, UserSeekerRating

def total_cancelled(user):
    return

def at_transaction_deletion(user, instance):
    if instance.provider == user:
        try:
            prov_rating = UserRating.objects.get(
                user=instance.provider
            )
            prov_rating.dislikes += 1
            prov_rating.save()
        except UserRating.DoesNotExist:
            UserRating.objects.create(
                user=instance.provider,
                dislikes = 1
            )
    else:
        try:
            seek_rating = UserSeekerRating.objects.get(
                user=instance.seeker
            )
            seek_rating.dislikes += 1
            seek_rating.save()
        except UserSeekerRating.DoesNotExist:
            UserSeekerRating.objects.create(
                user=instance.seeker,
                dislikes = 1
            )
    return


def at_transaction_completion(user, instance):
    # User Rating
    try:
        prov_data = UserRating.objects.get(
            user=instance.provider
        )
        prov_data.no_of_transaction += 1
        prov_data.total_amount_of_transaction += instance.total_amount
        prov_data.save()

    except UserRating.DoesNotExist:
        UserRating.objects.create(
            user=instance.provider,
            no_of_transaction=1,
            total_amount_of_transaction=instance.total_amount
        )

    # user as seeker rating
    try:
        seek_data = UserSeekerRating.objects.get(
            user=instance.seeker
        )
        seek_data.no_of_transaction += 1
        seek_data.total_amount_of_transaction += instance.total_amount
        seek_data.save()
    except UserSeekerRating.DoesNotExist:
        UserSeekerRating.objects.create(
            user=instance.provider,
            no_of_transaction=1,
            total_amount_of_transaction=instance.total_amount
        )

    return
