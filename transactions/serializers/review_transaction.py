from rest_framework import exceptions, serializers, validators
from ..models import *


class TransactionReviewSerializer(serializers.ModelSerializer):
    transaction_no = serializers.CharField(write_only=True)
    review_message = serializers.CharField(source="message")

    class Meta:
        model = TransactionReview
        fields = ("id", "transaction_no", "rating", "review_message",)
        read_only_fields =["id"]


    def create(self, validated_data):
        print(validated_data)
        transaction_no = validated_data.pop("transaction_no")
        transaction_id = transaction_no[8:]
        rating = validated_data.pop("rating")
        message = validated_data.pop("message")

        transaction = Transaction.objects.get(id=transaction_id)
        review = TransactionReview.objects.create(
            transaction_id=transaction.id,
            provider=transaction.provider,
            seeker=transaction.seeker,
            rating=rating,
            message=message
        )
        print(review)
        return review


class TransactionReviewRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionReview
        fields = ("transaction",)

