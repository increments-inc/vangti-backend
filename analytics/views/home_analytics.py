from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..models import *
from ..serializers import *
from django.db.models import Avg, Sum, Count
from transactions.models import TransactionHistory
from web_socket.models import LocationRadius
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db.models import Q


class HomeAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = UserRating.objects.all()
    serializer_class = UserRatingSerializer

    def seeker_analytics(self, *args, **kwargs):
        user = self.request.user
        # user_list = user.user_location_radius.user_list["users"]
        user_list = cache.get(f"{user.phone_number}")
        count_user = len(user_list)
        ratings = UserRating.objects.filter(user__phone_number__in=user_list, user__user_mode__is_provider=True)
        user_ratings = ratings.aggregate(
            Avg("deal_success_rate"),
            Avg("total_amount_of_transaction"),
            Avg("dislikes"),
            Avg("rating"),
            Avg("provider_response_time"),
        )
        deal_success_rate = user_ratings["deal_success_rate"]
        # total_amount_of_transaction = user_ratings["total_amount_of_transaction"]
        # dislikes = user_ratings["dislikes"]
        rating = user_ratings["rating"]
        provider_response_time = user_ratings["provider_response_time"]

        data = {
            "total_active_provider": count_user,
            "avg_deal_success_rate": deal_success_rate ,
            "avg_provider_rating": rating ,
            "avg_provider_response_time": provider_response_time,
        }
        return data

    def provider_analytics(self, *args, **kwargs):
        user = self.request.user
        user_list = cache.get(f"{user.phone_number}")
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
            created_at__gte=datetime.now() - timedelta(days=30),
            seeker__phone_number__in=user_list,
            seeker__user_mode__is_provider=False
        ).aggregate(Avg("total_amount"))
        avg_demanded = t_history["total_amount__avg"]
        avg_deal_possibility = 0
        if total_providers == 0 and total_seekers > 0:
            avg_deal_possibility = 100
        # check
        elif total_providers > 0 and total_seekers > 0:
            avg_deal_possibility = 1 / total_providers * 100

        data = {
            "avg_demanded_vangti": avg_demanded,
            "avg_deal_possibility": avg_deal_possibility
        }
        return data

    def home_analytics(self, request, *args, **kwargs):
        user = request.user
        mode = user.user_mode.is_provider
        if mode:
            data = self.provider_analytics()
        else:
            data = self.seeker_analytics()
        return Response(data, status=status.HTTP_200_OK)
