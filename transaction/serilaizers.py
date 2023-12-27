from rest_framework import exceptions, serializers, validators
from .models import *


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class TransactionReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionReview
        fields = "__all__"


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = "__all__"


class UserServiceModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserServiceMode
        fields = ("is_provider",)
