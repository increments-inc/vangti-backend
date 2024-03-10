from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from .transaction import Transaction
from utils.helper import secret_encode

User = get_user_model()


class TransactionAsProviderReview(BaseModel):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="txn_provider_review_provider"
    )
    rating = models.FloatField(default=0.0)
    message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("transaction",)


class TransactionAsSeekerReview(BaseModel):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="txn_seeker_review_seeker"
    )
    rating = models.FloatField(default=0.0)
    message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("transaction",)


class TransactionMessages(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="transaction_messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction_messages_user")
    message = models.TextField(null=True, blank=True)
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at", "transaction",)

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.message = secret_encode(self.message)
        super().save(*args, **kwargs)


class TransactionAsProviderAbuseReport(BaseModel):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="txn_prov_abuse_rep_provider"
    )
    message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("transaction",)


class TransactionAsSeekerAbuseReport(BaseModel):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="txn_seek_abuse_rep_seeker"
    )
    message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("transaction",)
