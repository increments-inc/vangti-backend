# from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from django.contrib.postgres.fields import ArrayField
import uuid

User = get_user_model()


class VangtiRequest(BaseModel):
    seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="vangti_seeker"
    )
    amount = models.FloatField(default=0.0)
    user_list = ArrayField(models.CharField(max_length=50))

    class Meta:
        abstract=True


class TransactionRequest(BaseModel):
    seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_transaction_seeker"
    )
    amount = models.FloatField(default=0.0)
    preferred_notes = ArrayField(models.CharField(max_length=50))
    is_affirmed = models.BooleanField(default=False)
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_transaction_provider"
    )

    class Meta:
        abstract=True
