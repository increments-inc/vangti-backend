from django.db.models import Q, Sum, Avg
from datetime import datetime, timedelta
from transactions.models import (
    CancelledTransaction, TransactionHistory,
    TransactionAsSeekerReview, TransactionAsProviderReview,
    TransactionAsSeekerAbuseReport, TransactionAsProviderAbuseReport,
    UserTransactionResponse
)
from analytics.models import UserRating, UserSeekerRating


def total_cancelled(user, as_provider: bool):
    if as_provider:
        total = CancelledTransaction.objects.filter(
            cancelled_by_provider=as_provider,
            provider=user
        ).count()
    else:
        total = CancelledTransaction.objects.filter(
            cancelled_by_provider=as_provider,
            seeker=user
        ).count()
    return {"total_cancelled": total}


def total_success(user, as_provider: bool):
    if as_provider:
        total = TransactionHistory.objects.filter(
            provider=user
        )
        total_count = total.count()
        total_data = total.aggregate(
            Sum('total_amount', default=0)
        )["total_amount__sum"]
    else:
        total = TransactionHistory.objects.filter(
            seeker=user
        )
        total_count = total.count()
        total_data = total.aggregate(
            Sum('total_amount', default=0)
        )["total_amount__sum"]
    return {"total_number": total_count, "total_amount": total_data}


def at_transaction_deletion(user, instance):
    if instance.provider == user:
        total_cancelled_count = total_cancelled(user, as_provider=True)["total_cancelled"]
        try:
            prov_rating = UserRating.objects.get(
                user=instance.provider
            )
            prov_rating.dislikes = total_cancelled_count
            prov_rating.save()
        except UserRating.DoesNotExist:
            UserRating.objects.create(
                user=instance.provider,
                dislikes=total_cancelled_count
            )
    else:
        total_cancelled_count = total_cancelled(user, as_provider=False)["total_cancelled"]
        try:
            seek_rating = UserSeekerRating.objects.get(
                user=instance.seeker
            )
            seek_rating.dislikes = total_cancelled_count
            seek_rating.save()
        except UserSeekerRating.DoesNotExist:
            UserSeekerRating.objects.create(
                user=instance.seeker,
                dislikes=total_cancelled_count
            )
    return


def at_transaction_completion(user, instance):
    # Provider Rating
    total_success_data = total_success(user, as_provider=True)
    print(total_success_data)
    #     return {"total_number": total_count, "total_amount": total_data}
    try:
        prov_data = UserRating.objects.get(
            user=instance.provider
        )
        prov_data.no_of_transaction = total_success_data["total_number"]
        prov_data.total_amount_of_transaction = total_success_data["total_amount"]
        prov_data.save()

    except UserRating.DoesNotExist:
        UserRating.objects.create(
            user=instance.provider,
            no_of_transaction=total_success_data["total_number"],
            total_amount_of_transaction=total_success_data["total_amount"]
        )

    # user as seeker rating
    total_success_data = total_success(user, as_provider=False)

    try:
        seek_data = UserSeekerRating.objects.get(
            user=instance.seeker
        )
        seek_data.no_of_transaction = total_success_data["total_number"]
        seek_data.total_amount_of_transaction = total_success_data["total_amount"]
        seek_data.save()
    except UserSeekerRating.DoesNotExist:
        UserSeekerRating.objects.create(
            user=instance.seeker,
            no_of_transaction=total_success_data["total_number"],
            total_amount_of_transaction=total_success_data["total_amount"]
        )

    return


def at_seeker_rating_update(user):
    all_reviews = TransactionAsSeekerReview.objects.filter(
        seeker=user
    ).aggregate(
        Avg("rating", default=0)
    )
    new_rating = (5 + all_reviews["rating__avg"]) / 2

    try:
        seek_data = UserSeekerRating.objects.get(
            user=user
        )
        seek_data.rating = new_rating
        seek_data.save()

    except UserSeekerRating.DoesNotExist:
        total_success_data = total_success(user, as_provider=False)
        UserSeekerRating.objects.create(
            user=user,
            no_of_transaction=total_success_data["total_number"],
            total_amount_of_transaction=total_success_data["total_amount"],
            rating=new_rating
        )

    return


def at_provider_rating_update(user):
    all_reviews = TransactionAsProviderReview.objects.filter(
        provider=user
    ).aggregate(
        Avg("rating", default=0)
    )

    try:
        prov_data = UserRating.objects.get(
            user=user
        )
        prov_data.rating = all_reviews["rating__avg"]
        prov_data.save()

    except UserRating.DoesNotExist:
        total_success_data = total_success(user, as_provider=True)
        UserRating.objects.create(
            user=user,
            no_of_transaction=total_success_data["total_number"],
            total_amount_of_transaction=total_success_data["total_amount"],
            rating=all_reviews["rating__avg"]
        )

    return


def at_seeker_abuse_rep_update(user):
    all_reviews = TransactionAsSeekerAbuseReport.objects.filter(
        seeker=user
    ).count()

    try:
        seek_data = UserSeekerRating.objects.get(
            user=user
        )
        seek_data.abuse_report_count = all_reviews
        seek_data.save()

    except UserSeekerRating.DoesNotExist:
        pass

    return


def at_provider_abuse_rep_update(user):
    all_reviews = TransactionAsProviderAbuseReport.objects.filter(
        provider=user
    ).count()

    try:
        prov_data = UserRating.objects.get(
            user=user
        )
        prov_data.abuse_report_count = all_reviews
        prov_data.save()

    except UserRating.DoesNotExist:
        pass

    return


def update_response_times_list(provider_list):
    for provider in provider_list:
        response_avg = UserTransactionResponse.objects.filter(
            provider=provider
        ).aggregate(Avg('response_duration', default=timedelta(seconds=0)))["response_duration__avg"]
        prov_rating = UserRating.objects.get(provider=provider)
        prov_rating.provider_response_time = response_avg
        prov_rating.save()
    return


def update_response_times(provider):
    response_avg = UserTransactionResponse.objects.filter(
        provider=provider
    ).aggregate(Avg('response_duration', default=timedelta(seconds=0)))["response_duration__avg"]
    prov_rating = UserRating.objects.get(user=provider)
    prov_rating.provider_response_time = response_avg
    prov_rating.save()
    return
