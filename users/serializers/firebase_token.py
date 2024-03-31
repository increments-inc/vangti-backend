from rest_framework import exceptions, serializers, validators
from .. import models


class UserFirebaseTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserFirebaseToken
        fields = ("id", "firebase_token",)

    def create(self, validated_data):
        user = self.context.get("request").user
        firebase_token= validated_data.get("firebase_token", None)

        try:
            ft = models.UserFirebaseToken.objects.get(
                user=user
            )
            ft.firebase_token = firebase_token
            ft.save()
        except models.UserFirebaseToken.DoesNotExist:
            ft = models.UserFirebaseToken.objects.create(
                user=user,
                firebase_token=firebase_token
            )
        return ft
