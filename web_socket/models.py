import uuid
from core.abstract_models import models, BaseModel
from django.contrib.auth import get_user_model
from transactions.models import Transaction

User = get_user_model()


class TransactionMessages(BaseModel):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="transaction_messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transaction_messages_user")
    message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("transaction", "-created_at",)

# class CallHistory(BaseModel):
#     transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name="room_call_history")
#     caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="call_history_caller")
#     callee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="call_history_callee")
#     duration = models.DurationField()
#
#     class Meta:
#         ordering = ("transaction", "-created_at",)
