from rest_framework import exceptions, serializers, validators
from ..models import *


class UserRatingSerializer(serializers.Serializer):
    total_active_provider = serializers.IntegerField(default=0)
    deal_success_rate = serializers.FloatField(default=0.0)
    rating = serializers.FloatField(default=0.0)
    dislikes = serializers.FloatField(default=0.0)
    provider_response_time = serializers.CharField(default="00:00:00")
    avg_demanded_vangti = serializers.CharField(default="0")
    avg_deal_possibility = serializers.FloatField(default=0.0)


class ProviderModeSerializer(serializers.ModelSerializer):
    total_deals_count = serializers.IntegerField(source="no_of_transaction")
    transaction_amount = serializers.FloatField(source="total_amount_of_transaction")
    deals_success_rate = serializers.FloatField(source="deal_success_rate")
    cancel_deals_count = serializers.IntegerField(source="dislikes")

    class Meta:
        model = UserRating
        fields = (
            "rating",
            "total_deals_count",
            "transaction_amount",
            "deals_success_rate",
            "cancel_deals_count",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if rep.get('rating') is None:
            rep['rating'] = 0.0
        else:
            rep['rating'] = round(rep['rating'], 1)
        if rep.get('transaction_amount') is None:
            rep['transaction_amount'] = 0.0
        if rep.get('total_deals_count') is None:
            rep['total_deals_count'] = 0
        if rep.get('deals_success_rate') is None:
            rep['deals_success_rate'] = 0.0
        if rep.get('cancel_deals_count') is None:
            rep['cancel_deals_count'] = 0
        return rep


class SeekerModeSerializer(serializers.ModelSerializer):
    total_deals_count = serializers.IntegerField(source="no_of_transaction")
    transaction_amount = serializers.FloatField(source="total_amount_of_transaction")
    deals_success_rate = serializers.FloatField(source="deal_success_rate")
    cancel_deals_count = serializers.IntegerField(source="dislikes")

    class Meta:
        model = UserSeekerRating
        fields = (
            "rating",
            "total_deals_count",
            "transaction_amount",
            "deals_success_rate",
            "cancel_deals_count",
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if rep.get('rating') is None:
            rep['rating'] = 0.0
        else:
            rep['rating'] = round(rep['rating'], 1)
        if rep.get('transaction_amount') is None:
            rep['transaction_amount'] = 0.0
        if rep.get('total_deals_count') is None:
            rep['total_deals_count'] = 0
        if rep.get('deals_success_rate') is None:
            rep['deals_success_rate'] = 0.0
        if rep.get('cancel_deals_count') is None:
            rep['cancel_deals_count'] = 0
        return rep
