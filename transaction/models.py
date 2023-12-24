from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import BaseModel
from django.contrib.postgres.fields import ArrayField
import uuid
User = get_user_model()


class Transaction(BaseModel):
    transaction_no = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        verbose_name="ID"
    )
    total_amount = models.FloatField()
    preferred_notes = ArrayField(ArrayField(models.CharField(max_length=10)))
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transaction_provider"
    )
    seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transaction_seeker"
    )
    charge = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    qr_image = models.ImageField()

    class Meta:
        ordering = ("-created_at",)


class TransactionHistory(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE,
                                    related_name="history_transaction")
    total_amount = models.FloatField()
    preferred_notes = ArrayField(ArrayField(models.CharField(max_length=10)))
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="history_provider"
    )
    seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="history_seeker"
    )
    charge = models.FloatField(default=0.0)

    class Meta:
        ordering = ("-created_at",)


class TransactionReview(BaseModel):
    REVIEW_STAR = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
    ]
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE,
                                    related_name="review_transaction")
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="review_provider"
    )
    seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="review_seeker"
    )
    rating = models.CharField(max_length=10, choices=REVIEW_STAR, null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

