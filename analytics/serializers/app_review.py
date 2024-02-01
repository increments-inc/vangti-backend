from rest_framework import exceptions, serializers, validators
from ..models import *


class AppFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppFeedback
        # fields = "__all__"
        exclude = ["user", ]

