# from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from .user_credit import CreditUser

User = get_user_model()


class ProviderTxnPlatform(BaseModel):
    transaction = models.IntegerField(primary_key=True, editable=True)
    provider = models.ForeignKey(CreditUser, on_delete=models.CASCADE, related_name='txn_platforms_provider')
    profit = models.FloatField(default=0.0)
    platform_fee = models.FloatField(default=0.0)

    def __str__(self):
        return self.transaction

    class Meta:
        ordering = ("transaction",)


class PlatformReceivable(BaseModel):
    user = models.ForeignKey(CreditUser, on_delete=models.CASCADE, related_name='platforms_receivable_user')
    amount = models.FloatField(default=0.0)

    def __str__(self):
        return self.user

    class Meta:
        ordering = ("user",)
