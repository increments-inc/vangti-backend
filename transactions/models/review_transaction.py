from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from .transaction import Transaction
from utils.helper import secret_encode
User = get_user_model()


class TransactionReview(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE,
                                    related_name="review_transaction")
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="review_provider"
    )
    seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="review_seeker"
    )
    rating = models.FloatField(default=0.0)
    message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class TransactionMessages(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="transaction_messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction_messages_user")
    message = models.TextField(null=True, blank=True)
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created_at", "transaction", )

    def save(self, *args, **kwargs):
        if self._state.adding:
            self.message = secret_encode(self.message)
        super().save(*args, **kwargs)
