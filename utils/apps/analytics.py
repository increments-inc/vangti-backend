import math
from django.db.models import Q, Sum, Avg, Count
from locations.models import UserLocation
from analytics.models import UserRating
from django.conf import settings
from django.contrib.gis.measure import D, Distance
from datetime import timedelta, time, datetime
from transactions.models import TransactionHistory


def calculate_user_impressions(user):
    no_of_transaction = user.userrating_user.no_of_transaction if user.userrating_user.no_of_transaction != 0 else 1
    deal_success_rate = user.userrating_user.deal_success_rate
    total_amount_of_transaction = user.userrating_user.total_amount_of_transaction
    cancelled_deals = user.userrating_user.dislikes
    rating = user.userrating_user.rating
    provider_response_time = user.userrating_user.provider_response_time
    acc_type = 1
    # if acc_type == "PERSONAL":
    #     acc_type = 1
    # if acc_type == "BUSINESS":
    #     acc_type = 10

    # print("here",
    #       deal_success_rate ,
    #       rating ,
    #       (1 / provider_response_time.total_seconds()) ,
    #       (total_amount_of_transaction / no_of_transaction) ,
    #       acc_type
    #       )

    user_impression = (
            deal_success_rate *
            rating *
            (1 / provider_response_time.total_seconds()) *
            (total_amount_of_transaction / no_of_transaction) *  # avg amount in transaction
            acc_type
    )
    # print(user.id, user_impression)
    return user_impression


def get_home_analytics_of_user_set(user_set):
    user_provider_set = user_set.filter(
        user_mode__is_provider=True
    )
    user_seeker_set = user_set.filter(
        user_mode__is_provider=False
    )
    total_providers = user_provider_set.count()
    total_seekers = user_seeker_set.count()
    rating_queryset = UserRating.objects.filter(user__in=user_set)

    # when nearby users have no rating set
    if not rating_queryset:
        return {
            "total_active_provider": 0,
            "deal_success_rate": 0.0,
            "rating": 0.0,
            "dislikes": 0,
            "provider_response_time": "0 sec",
            "avg_demanded_vangti": "0",
            "avg_deal_possibility": 0.0
        }
    # print("rating_queryset", rating_queryset.values())

    rating_queryset = rating_queryset.aggregate(
        Avg("deal_success_rate", default=0.0),
        Avg("rating", default=0.0),
        Avg("dislikes", default=0),
        Avg("provider_response_time", default=timedelta(seconds=0))
    )
    # print("rating_queryset232323", rating_queryset)

    time_dur = rating_queryset["provider_response_time__avg"].days * 3600 + rating_queryset[
        "provider_response_time__avg"].seconds
    if time_dur > 3600:
        time_dur /= 3600
        time_dur = f"{int(time_dur)} hr"
    elif time_dur > 60:
        time_dur /= 60
        time_dur = f"{int(time_dur)} min"
    else:
        time_dur = f"{time_dur} sec"
    # t_history = TransactionHistory.objects.filter(
    #     created_at__gte=datetime.now() - timedelta(days=90),
    #     provider__in=user_set,
    # ).aggregate(Avg("total_amount"))
    avg_deal_possibility = 0
    if (total_providers == 0) or (total_seekers == 0):
        avg_deal_possibility = 0
    # check
    elif total_providers > 0 and total_seekers > 0:
        if total_providers >= total_seekers:
            avg_deal_possibility = (total_seekers / total_providers) * 100
        else:
            avg_deal_possibility = 100
        # avg_deal_possibility = (1 / total_providers) * 100

    # total amount
    t_history = list(TransactionHistory.objects.filter(
        created_at__gte=datetime.now() - timedelta(days=90),
        provider__in=user_set,
    ).values_list("total_amount", flat=True))
    avg_demanded = "0" if len(t_history) == 0 else max(t_history, key=t_history.count)

    return {
        "total_active_provider": total_providers,
        "deal_success_rate": rating_queryset["deal_success_rate__avg"],
        "rating": rating_queryset["rating__avg"],
        "dislikes": math.ceil(rating_queryset["dislikes__avg"]),
        "provider_response_time": time_dur,
        "avg_demanded_vangti": f"{avg_demanded}",
        "avg_deal_possibility": float(avg_deal_possibility)
    }
