from rest_framework import exceptions, serializers, validators
from ..models import *
from users.models import VerifiedUsers
from drf_spectacular.utils import extend_schema_field


class UserServiceModeSerializer(serializers.ModelSerializer):
    kyc_enabled = serializers.SerializerMethodField()

    class Meta:
        model = UserServiceMode
        fields = ("is_provider", "kyc_enabled",)
        # read_only_fields =("kyc_enabled",)

    @extend_schema_field(serializers.BooleanField)
    def get_kyc_enabled(self, obj):
        user = self.context.get("request").user
        if VerifiedUsers.objects.filter(user=user).exists():
            return True
        # real state
        # return False
        # disabled kyc dependency
        return True



# class UserServiceModeChangeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserServiceMode
#         fields = ("is_provider",)
