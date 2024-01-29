from rest_framework import exceptions, serializers, validators
from ..models import *


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class TransactionSeekerHistorySerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source="provider.user_info.person_name", read_only=True)
    total_amount__of_transactions = serializers.FloatField(source="provider.userrating_user.no_of_transaction",
                                                           read_only=True)
    rating = serializers.FloatField(source="provider.userrating_user.rating", read_only=True)
    dislikes = serializers.IntegerField(source="provider.userrating_user.dislikes", read_only=True)
    deal_success_rate = serializers.FloatField(source="provider.userrating_user.deal_success_rate", read_only=True)

    class Meta:
        model = TransactionHistory
        fields = (
            "id",
            "total_amount",
            "preferred_notes",
            "created_at",

            "provider_name",
            "total_amount__of_transactions",
            "rating",
            "dislikes",
            "deal_success_rate",
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret["provider_name"] is None:
            ret['provider_name'] = ""
        if ret["total_amount__of_transactions"] is None:
            ret['total_amount__of_transactions'] = float(0)
        if ret["rating"] is None:
            ret['rating'] = float(0)
        if ret["dislikes"] is None:
            ret['dislikes'] = 0
        if ret["deal_success_rate"] is None:
            ret['deal_success_rate'] = float(0)
        return ret


class TransactionProviderHistorySerializer(serializers.ModelSerializer):
    seeker_name = serializers.CharField(source="seeker.user_info.person_name", read_only=True)
    total_deals = serializers.IntegerField(source="seeker.userrating_user.no_of_transaction", read_only=True)
    rating = serializers.FloatField(source="seeker.userrating_user.rating", read_only=True)

    class Meta:
        model = TransactionHistory
        fields = (
            "id",
            "total_amount",
            "preferred_notes",
            "created_at",
            "seeker_name",
            "total_deals",
            "rating",
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret["seeker_name"] is None:
            ret['seeker_name'] = ""
        if ret["total_deals"] is None:
            ret['total_deals'] = 0
        if ret["rating"] is None:
            ret['rating'] = float(0)
        return ret
