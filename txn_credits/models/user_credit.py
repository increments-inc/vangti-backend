from django.contrib.gis.db import models
from core.abstract_models import BaseModel
import uuid


class CreditUser(BaseModel):
    user_uid = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4, editable=True)

    class Meta:
        ordering = ("user_uid",)

    def __str__(self):
        return f"{self.user_uid}"


class AccumulatedCredits(BaseModel):
    user = models.OneToOneField(CreditUser, on_delete=models.CASCADE)
    credit_as_seeker = models.FloatField(default=0)
    credit_as_provider = models.FloatField(default=0)

    class Meta:
        ordering = ("user",)

    def __str__(self):
        return f"{self.user.user_uid}"
