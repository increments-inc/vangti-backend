from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.geos import Point, LineString
from core.abstract_models import BaseModel
import uuid

User = get_user_model()


class TxnCredits(BaseModel):
    txn_id = models.IntegerField(primary_key=True)
    charge = models.FloatField(default=0)
    credit = models.FloatField(default=0)
    txn_completed = models.BooleanField(default=False)



