# from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from django.contrib.postgres.fields import ArrayField
import uuid

User = get_user_model()


class Transaction(BaseModel):
    # transaction_no = models.UUIDField(
    #     default=uuid.uuid4
    # )
    transaction_no = models.CharField(max_length=255, null=True, blank=True)
    total_amount = models.FloatField(default=0, null=True)
    preferred_notes = ArrayField(ArrayField(models.CharField(max_length=10, null=True, blank=True)))
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transaction_provider", null=True
    )
    seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transaction_seeker", null=True
    )
    charge = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    qr_image = models.ImageField(null=True, blank=True)

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


class DigitalWallet(BaseModel):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="digitalwallet_transaction"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="digitalwallet_user"
    )
    charge = models.FloatField(default=0.0)
    amount = models.FloatField(default=0.0)
    system_fee = models.FloatField(default=0.0)

    def __str__(self):
        return self.user.phone_number
