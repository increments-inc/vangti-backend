from rest_framework import (
    permissions,
    response,
    status,
    viewsets,
)
from ..serializers import *
from django.db.models import Q, Sum, Avg, Count
from ..tasks import *
from locations.models import UserLocation
from analytics.models import UserRating
from django.conf import settings
from django.contrib.gis.measure import D, Distance
from datetime import timedelta, time


# def get_user_analytics()
def get_mode_user_list(user):
    center = UserLocation.objects.using('location').get(user=user.id).centre
    radius = settings.LOCATION_RADIUS
    user_location_list = list(
        UserLocation.objects.using('location').filter(
            centre__distance_lte=(center, Distance(km=radius))
        ).values_list(
            "user", flat=True
        )
    )
    user_provider_list = list(
        User.objects.filter(
            is_superuser=False,
            id__in=user_location_list,
            # user_mode__is_provider=True
        ).order_by(
            "-userrating_user__rating"
        )
        # .values_list(
        #     'id', flat=True
        # )
    )
    # user_list = [str(id) for id in user_provider_list]
    return user_provider_list


def get_user_list(user):
    center = UserLocation.objects.using('location').get(user=user.id).centre
    radius = settings.LOCATION_RADIUS
    user_location_list = list(
        UserLocation.objects.using('location').filter(
            centre__distance_lte=(center, Distance(km=radius))
        ).values_list(
            "user", flat=True
        )
    )
    if user.user_mode.is_provider:
        print("provider tru")
        user_provider_list = list(
            User.objects.filter(
                is_superuser=False,
                id__in=user_location_list,
                user_mode__is_provider=False
            ).order_by(
                "-userrating_user__rating"
            )
            # .values_list(
            #     'id', flat=True
            # )
        )
    else:
        print("provider fal")

        user_provider_list = list(
            User.objects.filter(
                is_superuser=False,
                id__in=user_location_list,
                user_mode__is_provider=True
            ).order_by(
                "-userrating_user__rating"
            )
            # .values_list(
            #     'id', flat=True
            # )
        )
    # user_list = [str(id) for id in user_provider_list]
    return user_provider_list


def get_user_analytics(user_list):
    ## total total_active_provider
    total_user = len(user_list)
    rating_queryset = UserRating.objects.filter(
        user__in=user_list
    ).annotate(
        avg_success_rate=Avg("deal_success_rate", default=0.0),
        avg_rating=Avg("rating", default=0.0),
        total_dislikes=Count("dislikes"),
        avg_response_time=Avg("provider_response_time", default=timedelta(seconds=1)),
    ).values("avg_success_rate", "avg_rating", "avg_response_time", "total_dislikes")
    time_duration = rating_queryset[0]["avg_response_time"]
    if time_duration.days == 0 and time_duration.seconds > 60:
        time_dur = f"{round(time_duration.seconds / 60, 2)} min"
    elif time_duration.days == 0 and time_duration.seconds < 60:
        time_dur = f"{time_duration.seconds} sec"
    elif time_duration.days != 0:
        time_dur = f"{round(time_duration.days * 24 + time_duration.seconds / 3600, 2)} hr"
    else:
        time_dur = f"{round(time_duration.days * 24 + time_duration.seconds / 3600, 2)} hr"

    print("rating", rating_queryset)
    return {

        "total_active_provider": total_user,
        "deal_success_rate": rating_queryset[0]["avg_success_rate"],
        "rating": rating_queryset[0]["avg_rating"],
        "dislikes": float(rating_queryset[0]["total_dislikes"]),
        "provider_response_time": time_dur,
        "avg_demanded_vangti": "1000",
        "avg_deal_possibility": 100.0
    }


class UserServiceModeViewSet(viewsets.ModelViewSet):
    queryset = UserServiceMode.objects.all()
    serializer_class = UserServiceModeSerializer
    permission_classes = [permissions.IsAuthenticated]

    # def get_serializer_class(self):
    #     if self.action == 'mode_change':
    #         return UserServiceModeChangeSerializer
    #     return self.serializer_class

    def get_mode(self, *args, **kwargs):
        serializer = self.serializer_class(self.queryset.get(user=self.request.user), context={'request': self.request})
        return response.Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def mode_change(self, *args, **kwargs):
        instance = self.queryset.get(user=self.request.user)
        data = self.request.data
        serializer = self.serializer_class(instance, data=data, context={"request": self.request})
        # kyc dependency
        # try:
        #     self.request.user.users_verified
        # except ObjectDoesNotExist:
        #     return response.Response(
        #         {"message": "User not verified"},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        if Transaction.objects.filter(
                Q(seeker=self.request.user) | Q(provider=self.request.user)
        ).filter(
            is_completed=False
        ).exists():
            print("open deals exists")
            return response.Response(
                {
                    "errors": "Cannot change mode while transaction is ongoing"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            self.perform_update(serializer)
            user_list = (get_mode_user_list(self.request.user))
            empty = []
            for usr in user_list:
                sur_user_list = get_user_list(usr)
                ana = get_user_analytics(sur_user_list)
                ana["user"] = str(usr.id)
                empty.append(ana)
            send_out_mesg.delay(empty)

            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return response.Response("", status=status.HTTP_400_BAD_REQUEST)
