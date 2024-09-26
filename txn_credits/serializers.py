from rest_framework import exceptions, serializers, validators
from .models import *


class CreditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditUser
        fields = '__all__'


class AccumulatedCreditsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccumulatedCredits
        fields = (
            "user",
            "credit_as_provider",
        )

