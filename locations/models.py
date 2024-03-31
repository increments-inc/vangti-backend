from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.geos import Point, LineString

import uuid

User = get_user_model()


class UserLocation(models.Model):
    # user = models.CharField(max_length=256, null=True, blank=True)
    user = models.UUIDField(unique=True)
    user_phone_number = models.CharField(max_length=15, blank=True, null=True)
    # latitude = models.CharField(max_length=10, default="0")
    # longitude = models.CharField(max_length=10, default="0")
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    centre = models.PointField()

    def __str__(self):
        try:
            return f"{self.user_phone_number}- {self.latitude}, {self.longitude}"
        except:
            return f"{self.user_phone_number}-location"

    class Meta:
        ordering = ("user",)

    def save(self, *args, **kwargs):
        self.centre = Point(float(self.longitude), float(self.latitude))
        super().save(*args, **kwargs)


class PolyLine(models.Model):
    transaction = models.IntegerField(null=True, blank=True)
    linestring = models.LineStringField(null=True, blank=True)

    seeker_location = models.PointField(null=True, blank=True)
    provider_location = models.PointField(null=True, blank=True)

    def __str__(self):
        return f"polyline {self.transaction}"

    class Meta:
        ordering = ("transaction",)
