from django.contrib.auth.models import User
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from django.db.models import Avg
from transactions.models import TransactionHistory
from datetime import datetime, timedelta
from django.contrib.gis.measure import Distance
from locations.models import UserLocation
from django.conf import settings
from ..serializers import *
from web_socket.fcm import send_push2


class HomeAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = UserRating.objects.all()
    serializer_class = UserRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_user_list(self, *args, **kwargs):
        user = self.request.user
        try:
            center = UserLocation.objects.using('location').get(user=user.id).centre
            user_location_list = list(
                UserLocation.objects.using('location').filter(
                    centre__distance_lte=(center, Distance(km=settings.LOCATION_RADIUS))
                ).values_list(
                    "user", flat=True
                )
            )
            print(user_location_list)
            user_provider_list = list(
                User.objects.filter(
                    id__in=user_location_list,
                    user_mode__is_provider=True
                ).exclude(
                    id=user.id,
                    is_superuser=True
                ).values_list(
                    'phone_number', flat=True
                )
            )
            print(user_provider_list)
            return user_provider_list
        except:
            return []

    def seeker_analytics(self, *args, **kwargs):
        user = self.request.user
        try:
            # user_list = cache.get(f"{user.phone_number}")
            user_list = self.get_user_list(*args, **kwargs)
            count_user = len(user_list)
            print(user_list)
            ratings = UserRating.objects.filter(user__phone_number__in=user_list, user__user_mode__is_provider=True)
            print(ratings)
            user_ratings = ratings.aggregate(
                Avg("deal_success_rate"),
                Avg("total_amount_of_transaction"),
                Avg("dislikes"),
                Avg("rating"),
                Avg("provider_response_time"),
            )
            deal_success_rate = user_ratings["deal_success_rate__avg"]
            rating = user_ratings["rating__avg"]
            provider_response_time = user_ratings["provider_response_time__avg"]
            if provider_response_time is None:
                provider_response_time = "00:00:00"
            data = {
                "total_active_provider": count_user,
                "avg_deal_success_rate": deal_success_rate,
                "avg_provider_rating": rating,
                "avg_provider_response_time": provider_response_time,
                "avg_demanded_vangti": "0",
                "avg_deal_possibility": 0.0
            }
            print("data", data)
        except:
            data = {
                "total_active_provider": 0,
                "avg_deal_success_rate": 0.0,
                "avg_provider_rating": 0.0,
                "avg_provider_response_time": "00:00:00",
                "avg_demanded_vangti": "0",
                "avg_deal_possibility": 0.0
            }
        return data

    def provider_analytics(self, *args, **kwargs):
        user = self.request.user
        try:
            user_list = self.get_user_list(*args, **kwargs)
            count_user = len(user_list)
            print(user_list, "user_list", count_user)
            nearby_users = User.objects.filter(
                phone_number__in=user_list,
            )
            total_seekers = nearby_users.filter(
                user_mode__is_provider=False
            ).count()
            total_providers = nearby_users.filter(
                user_mode__is_provider=True
            ).count()
            t_history = TransactionHistory.objects.filter(
                created_at__gte=datetime.now() - timedelta(days=90),
                seeker__phone_number__in=user_list,
                seeker__user_mode__is_provider=False
            ).aggregate(Avg("total_amount"))
            print(t_history)
            avg_demanded = t_history["total_amount__avg"]
            avg_deal_possibility = 0
            if total_providers == 0 and total_seekers > 0:
                avg_deal_possibility = 100
            # check
            elif total_providers > 0 and total_seekers > 0:
                avg_deal_possibility = 1 / total_providers * 100

            if avg_demanded is None:
                avg_demanded = 0

            data = {
                "total_active_provider": 0,
                "avg_deal_success_rate": 0.0,
                "avg_provider_rating": 0.0,
                "avg_provider_response_time": "00:00:00",
                "avg_demanded_vangti": str(avg_demanded),
                "avg_deal_possibility": avg_deal_possibility
            }
        except:
            data = {
                "total_active_provider": 0,
                "avg_deal_success_rate": 0.0,
                "avg_provider_rating": 0.0,
                "avg_provider_response_time": "00:00:00",
                "avg_demanded_vangti": "0",
                "avg_deal_possibility": 0.0
            }
        return data

    def home_analytics(self, request, *args, **kwargs):
        user = request.user
        # send_push2(user, user, {})
        mode = user.user_mode.is_provider
        if mode:
            data = self.provider_analytics()
        else:
            data = self.seeker_analytics()
        return Response(data, status=status.HTTP_200_OK)
