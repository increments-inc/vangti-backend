# from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from django.contrib.postgres.fields import ArrayField
import uuid

User = get_user_model()


class TransactionRequest(BaseModel):
    REQUEST_STATUS = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected")
    ]
    seeker = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_transaction_seeker"
    )
    amount = models.FloatField(default=0.0)
    preferred_notes = ArrayField(models.CharField(max_length=50, null=True, blank=True))
    # is_affirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=REQUEST_STATUS, default="PENDING")
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_transaction_provider", null=True
    )

    class Meta:
        abstract = True
        ordering = ("seeker",)
