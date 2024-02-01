from rest_framework import exceptions, serializers, validators
from ..models import *


class UserRatingSerializer(serializers.Serializer):
    total_active_provider = serializers.IntegerField(default=0)
    deal_success_rate = serializers.FloatField(default=0.0)
    rating = serializers.FloatField(default=0.0)
    dislikes = serializers.FloatField(default=0.0)
    provider_response_time = serializers.CharField(default="00:00:00")
    avg_demanded_vangti = serializers.CharField(default="0")
    avg_deal_possibility = serializers.FloatField(default=0.0)
