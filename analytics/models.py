from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import BaseModel
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


class UserRating(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="userrating_user"
    )
    deal_success_rate = models.FloatField(default=0.0)
    total_amount_of_transaction = models.FloatField(default=0.0)
    dislikes = models.IntegerField(default=0)
    rating = models.CharField(max_length=10, choices=REVIEW_STAR, null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)


class AppFeedback(BaseModel):
    rating = models.CharField(max_length=10, choices=REVIEW_STAR, null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="appfeedback_user"
    )
    message = models.TextField(null=True, blank=True)
