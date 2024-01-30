from rest_framework import exceptions, serializers, validators
from .. import models


class UserFirebaseTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserFirebaseToken
        fields = ("id", "firebase_token",)
