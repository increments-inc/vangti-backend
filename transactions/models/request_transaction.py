# from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from django.contrib.postgres.fields import ArrayField

User = get_user_model()


class UserTransactionResponse(BaseModel):
    seeker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_transaction_response_seeker"
    )
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_transaction_response_provider"
    )
    response_time = models.DateTimeField(null=True, blank=True)
    response_duration = models.DurationField(null=True, blank=True)

    class Meta:
        ordering = ("provider",)

    def save(self, *args, **kwargs):
        # super().save(*args, **kwargs)

        if self.response_time is not None:
            self.response_duration = self.response_time - self.created_at
        super().save(*args, **kwargs)


class UserOnTxnRequest(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ("user",)

    def __str__(self):
        return f"{self.user.id}"

