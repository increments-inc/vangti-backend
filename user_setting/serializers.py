from rest_framework import exceptions, serializers, validators
from .models import *


class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = "__all__"


class UserLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = ("language",)


class UserTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = ("accepted_terms", "accepted_timestamp",)


class VangtiTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VangtiTerms
        fields = "__all__"
