from rest_framework import exceptions, serializers, validators
from .models import *





class UserRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRating
        fields = "__all__"


class AppFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppFeedback
        # fields = "__all__"
        exclude = ["user",]


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

