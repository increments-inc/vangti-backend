# from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from .user_credit import CreditUser, AccumulatedCredits

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            platform_receivable = PlatformReceivable.objects.using("credits").get(
                user=self.provider
            )
            platform_receivable.amount += self.platform_fee
            platform_receivable.save()
        except PlatformReceivable.DoesNotExist:
            PlatformReceivable.objects.using("credits").create(
                user=self.provider,
                amount=self.platform_fee
            )


class PlatformReceivable(BaseModel):
    user = models.ForeignKey(CreditUser, on_delete=models.CASCADE, related_name='platforms_receivable_user')
    amount = models.FloatField(default=0.0)

    def __str__(self):
        return self.user

    class Meta:
        ordering = ("user",)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            user_acc_credit = AccumulatedCredits.objects.using("credits").get(
                user=self.user
            )
            user_acc_credit.credit_as_provider = -abs(self.amount)
            user_acc_credit.save()
        except AccumulatedCredits.DoesNotExist:
            AccumulatedCredits.objects.using("credits").create(
                user=self.user,
                credit_as_provider=-abs(self.amount)
            )
