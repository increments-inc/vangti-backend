from rest_framework import exceptions, serializers, validators
from .models import *


class HomeAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analytics
        fields = "__all__"


class UserRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRating
        fields = "__all__"


class AppFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppFeedback
        # fields = "__all__"
        exclude = ["user",]
