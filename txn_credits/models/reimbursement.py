from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.geos import Point, LineString
from core.abstract_models import BaseModel
import uuid

User = get_user_model()


# class Reimbursement(BaseModel):
#     user = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4, editable=True)
#     credit_as_seeker = models.FloatField(default=0)
#     credit_as_provider = models.FloatField(default=0)
#
#     class Meta:
#         ordering = ("user",)


