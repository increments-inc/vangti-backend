from rest_framework import exceptions, serializers, validators
from .models import *


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = "__all__"


class UserServiceModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserServiceMode
        fields = ("is_provider",)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class TransactionReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionReview
        fields = ("id", "transaction", "rating", "message",)

    def create(self, validated_data):
        transaction_id_no = validated_data.pop("transaction")

        rating = validated_data.pop("rating")
        message = validated_data.pop("message")

        transaction = Transaction.objects.get(id=transaction_id_no.id)
        review = TransactionReview.objects.create(
            transaction_id=transaction.id,
            provider=transaction.provider,
            seeker=transaction.seeker,
            rating=rating,
            message=message
        )
        return review


class TransactionReviewRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionReview
        fields = ("transaction",)

