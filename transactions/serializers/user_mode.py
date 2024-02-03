from rest_framework import exceptions, serializers, validators
from ..models import *
from users.models import VerifiedUsers


class UserServiceModeSerializer(serializers.ModelSerializer):
    kyc_enabled = serializers.BooleanField(default=True, read_only=True)

    class Meta:
        model = UserServiceMode
        fields = ("is_provider", "kyc_enabled",)
        # read_only_fields =("kyc_enabled",)

    def get_kyc_enabled(self, obj):
        user = self.context.get("request").user
        if VerifiedUsers.objects.filter(user=user).exists():
            return True
        return False


# class UserServiceModeChangeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserServiceMode
#         fields = ("is_provider",)
