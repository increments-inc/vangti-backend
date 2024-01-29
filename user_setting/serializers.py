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
        fields = ("terms_and_conditions", "privacy_policy", "about")

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        term_path = ret["terms_and_conditions"][1:]
        with open(term_path, "r") as f1:
            tt = f1.read()
            ret["terms_and_conditions"] = tt
        pri_path = ret["privacy_policy"][1:]
        with open(pri_path, "r") as f1:
            tt = f1.read()
            ret["privacy_policy"] = tt
        about_path = ret["about"][1:]
        with open(about_path, "r") as f1:
            tt = f1.read()
            ret["about"] = tt

        return ret


