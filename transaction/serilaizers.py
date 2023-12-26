from rest_framework import exceptions, serializers, validators
from .models import *


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class UserServiceModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserServiceMode
        fields = ("is_provider", )
