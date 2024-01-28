from rest_framework import exceptions, serializers, validators
from .models import *


class UserRatingSerializer(serializers.Serializer):
    total_active_provider = serializers.IntegerField(default=0)
    deal_success_rate = serializers.FloatField(default=0.0)
    rating = serializers.FloatField(default=0.0)
    dislikes = serializers.FloatField(default=0.0)
    provider_response_time = serializers.CharField(default = "00:00:00")
    avg_demanded_vangti = serializers.CharField(default="0")
    avg_deal_possibility= serializers.FloatField(default=0.0)


class AppFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppFeedback
        # fields = "__all__"
        exclude = ["user", ]


class InsightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analytics
        fields = "__all__"
        read_only_fields = ["user", "update_at", ]

    # def to_representation(self, value):
    #     print(value)
    #     print("helo")
    #     # if value.created_at:
    #     #     print(value.created_at)
    #     return value.profit
    #     # raise Exception('Unexpected type of tagged object')
