# from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from django.contrib.postgres.fields import ArrayField
import uuid

User = get_user_model()

REVIEW_STAR = [
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4", "4"),
    ("5", "5"),
]


class Analytics(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="analytics_user"
    )
    no_of_transaction = models.IntegerField(default=0)
    profit = models.FloatField(default=0.0)
    total_amount_of_transaction = models.FloatField(default=0.0)

    class Meta:
        ordering = ("-created_at",)


# foreign key/ one to one
class UserRating(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="userrating_user"
    )
    no_of_transaction = models.IntegerField(default=0)
    deal_success_rate = models.FloatField(default=0.0)
    total_amount_of_transaction = models.FloatField(default=0.0)
    dislikes = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    provider_response_time = models.DurationField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class AppFeedback(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="appfeedback_user"
    )
    rating = models.FloatField(default=0.0)
    message = models.TextField(null=True, blank=True)
