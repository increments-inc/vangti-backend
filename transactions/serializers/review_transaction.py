from rest_framework import exceptions, serializers, validators
from ..models import *
from utils.apps.transaction import get_transaction_id
from utils.helper import secret_decode


class TransactionMessagesSerializer(serializers.ModelSerializer):
    user_role = serializers.SerializerMethodField()

    class Meta:
        model = TransactionMessages
        fields = (
            "created_at",
            "message",
            "user",
            "user_role"
        )

    def get_user_role(self, obj):
        role = None
        if obj.transaction.seeker == obj.user:
            role = "seeker"
        if obj.transaction.provider == obj.user:
            role = "provider"
        return role

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if "message" in rep:
            rep["message"] = secret_decode(rep["message"])
        return rep


class TransactionAsSeekerReviewSerializer(serializers.ModelSerializer):
    transaction_no = serializers.CharField(source="transaction.get_transaction_unique_no")
    review_message = serializers.CharField(source="message", required=False, allow_null=True)

    class Meta:
        model = TransactionAsSeekerReview
        fields = ("transaction_no", "rating", "review_message",)

    def create(self, validated_data):
        print(validated_data)
        user = self.context.get("request").user
        transaction_no = validated_data.pop("transaction")["get_transaction_unique_no"]
        transaction_id = get_transaction_id(transaction_no)
        try:
            transaction_instance = Transaction.objects.get(id=int(transaction_id))
        except:
            return -1

        rating = validated_data.pop("rating")
        message = validated_data.pop("message")

        if transaction_instance.seeker != user:
            return -2
        try:
            review = TransactionAsSeekerReview.objects.get(
                transaction=transaction_instance,
                provider=transaction_instance.provider,
                seeker=transaction_instance.seeker
            )
            review.rating = rating
            review.message = message
            review.save()
        except TransactionAsSeekerReview.DoesNotExist:
            review = TransactionAsSeekerReview.objects.create(
                transaction=transaction_instance,
                provider=transaction_instance.provider,
                seeker=transaction_instance.seeker,
                rating=rating,
                message=message
            )
        return review


class TransactionAsProviderReviewSerializer(serializers.ModelSerializer):
    transaction_no = serializers.CharField(source="transaction.get_transaction_unique_no")
    review_message = serializers.CharField(source="message",required=False, allow_null=True)

    class Meta:
        model = TransactionAsProviderReview
        fields = ("transaction_no", "rating", "review_message",)

    def create(self, validated_data):
        print(validated_data)
        user = self.context.get("request").user
        transaction_no = validated_data.pop("transaction")["get_transaction_unique_no"]
        transaction_id = get_transaction_id(transaction_no)
        try:
            transaction_instance = Transaction.objects.get(id=int(transaction_id))
        except:
            return -1

        rating = validated_data.pop("rating")
        message = validated_data.pop("message", None)

        if transaction_instance.provider != user:
            return -2
        try:
            review = TransactionAsProviderReview.objects.get(
                transaction=transaction_instance,
                provider=transaction_instance.provider,
                seeker=transaction_instance.seeker
            )
            review.rating = rating
            review.message = message
            review.save()
        except TransactionAsProviderReview.DoesNotExist:
            review = TransactionAsProviderReview.objects.create(
                transaction=transaction_instance,
                provider=transaction_instance.provider,
                seeker=transaction_instance.seeker,
                rating=rating,
                message=message
            )
        return review


class TransactionAsProviderAbuseReportSerializer(serializers.ModelSerializer):
    transaction_no = serializers.CharField(source="transaction.get_transaction_unique_no")
    review_message = serializers.CharField(source="message")

    class Meta:
        model = TransactionAsProviderAbuseReport
        fields = ("transaction_no", "review_message",)

    def create(self, validated_data):
        user = self.context.get("request").user
        transaction_no = validated_data.pop("transaction")["get_transaction_unique_no"]
        transaction_id = get_transaction_id(transaction_no)
        try:
            transaction_instance = Transaction.objects.get(id=int(transaction_id))
        except:
            return -1

        message = validated_data.pop("message")

        if transaction_instance.provider != user:
            return -2
        try:
            review = TransactionAsProviderAbuseReport.objects.get(
                transaction=transaction_instance,
                provider=transaction_instance.provider,
                seeker=transaction_instance.seeker
            )
            review.message = message
            review.save()
        except TransactionAsProviderAbuseReport.DoesNotExist:
            review = TransactionAsProviderAbuseReport.objects.create(
                transaction=transaction_instance,
                provider=transaction_instance.provider,
                seeker=transaction_instance.seeker,
                message=message
            )
        return review


class TransactionAsSeekerAbuseReportSerializer(serializers.ModelSerializer):
    transaction_no = serializers.CharField(source="transaction.get_transaction_unique_no")
    review_message = serializers.CharField(source="message")

    class Meta:
        model = TransactionAsSeekerAbuseReport
        fields = ("transaction_no", "review_message",)

    def create(self, validated_data):
        user = self.context.get("request").user
        transaction_no = validated_data.pop("transaction")["get_transaction_unique_no"]
        transaction_id = get_transaction_id(transaction_no)
        try:
            transaction_instance = Transaction.objects.get(id=int(transaction_id))
        except:
            return -1

        message = validated_data.pop("message")

        if transaction_instance.seeker != user:
            return -2
        try:
            review = TransactionAsSeekerAbuseReport.objects.get(
                transaction=transaction_instance,
                provider=transaction_instance.provider,
                seeker=transaction_instance.seeker
            )
            review.message = message
            review.save()
        except TransactionAsSeekerAbuseReport.DoesNotExist:
            review = TransactionAsSeekerAbuseReport.objects.create(
                transaction=transaction_instance,
                provider=transaction_instance.provider,
                seeker=transaction_instance.seeker,
                message=message
            )
        return review
