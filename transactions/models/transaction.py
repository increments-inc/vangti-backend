# from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from django.contrib.postgres.fields import ArrayField
import uuid
from utils import qr
from django.contrib.sites.models import Site
from django.core.files import File
from datetime import datetime
from utils.helper import content_file_path, ImageCompress
from utils.apps.transaction import get_transaction_no, generate_transaction_pin
User = get_user_model()


class Transaction(BaseModel):
    # transaction_no = models.UUIDField(
    #     default=uuid.uuid4
    # )
    # transaction_no = models.CharField(max_length=255, null=True, blank=True)
    total_amount = models.FloatField(default=0, null=True)
    preferred_notes = ArrayField(models.CharField(max_length=10, null=True, blank=True))
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transaction_provider", null=True
    )
    seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transaction_seeker", null=True
    )
    charge = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    qr_image = models.ImageField(upload_to=content_file_path, null=True, blank=True)
    transaction_pin = models.CharField(default="", blank=True, max_length=10)

    class Meta:
        ordering = ("-created_at", "-id",)

    @property
    def get_transaction_unique_no(self):
        return get_transaction_no(self.id, self.created_at)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.qr_image and self._state.adding==False:
            self.transaction_pin = generate_transaction_pin()
            url = f"{self.transaction_pin}"
            image_stream = qr.generate(url)
            self.qr_image = File(image_stream, name=f"qr.png")
            self.save(update_fields=["qr_image", "transaction_pin"])


class TransactionHistory(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE,
                                    related_name="history_transaction")
    total_amount = models.FloatField()
    preferred_notes = ArrayField(models.CharField(max_length=10))
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
