# from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from django.contrib.postgres.fields import ArrayField
import uuid
from utils import qr
from django.contrib.sites.models import Site
from django.core.files import File
from datetime import datetime

User = get_user_model()


class Transaction(BaseModel):
    # transaction_no = models.UUIDField(
    #     default=uuid.uuid4
    # )
    # transaction_no = models.CharField(max_length=255, null=True, blank=True)
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
        ordering = ("-created_at", "-id",)

    @property
    def get_transaction_unique_no(self):
        return f"{self.created_at.date().strftime('%Y%m%d')}{self.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if  not self.qr_image and self._state.adding==False:
            # self.created_at.date().strftime('%Y%m%d') + self.id
            current_site = Site.objects.get_current()

            # url = f"http://{current_site.domain}/api/transaction/{self.get_transaction_unique_no}/?status=completed"
            url = f"{self.get_transaction_unique_no}"
            image_stream = qr.generate(url)
            self.qr_image = File(image_stream, name=f"qr.png")
            self.save(update_fields=["qr_image"])


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
