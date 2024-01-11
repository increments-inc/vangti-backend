from rest_framework import exceptions, serializers, validators
from ..models import *


class UserServiceModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserServiceMode
        fields = ("is_provider",)