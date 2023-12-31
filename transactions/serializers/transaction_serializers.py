from rest_framework import exceptions, serializers, validators
from ..models import *


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = "__all__"


class UserServiceModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserServiceMode
        fields = ("is_provider",)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


