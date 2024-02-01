from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.geos import Point

import uuid

User = get_user_model()


class UserLocation(models.Model):
    # user = models.CharField(max_length=256, null=True, blank=True)
    user = models.UUIDField(unique=True)
    user_phone_number = models.CharField(max_length=15, blank=True, null=True)
    latitude = models.CharField(max_length=10, default="0")
    longitude = models.CharField(max_length=10, default="0")
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


class LocationRadius(models.Model):
    location = models.OneToOneField(
        UserLocation, on_delete=models.CASCADE, related_name="location_radius_userlocation"
    )
    user_id_list = ArrayField(models.CharField(max_length=256))

    def __str__(self):
        try:
            return f"{self.location.user}"
        except:
            return "None"

    class Meta:
        abstract=True
        ordering = ("location",)

# abstract models
# class UserLocation(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_location")
#     latitude = models.CharField(max_length=10, null=True, blank=True)
#     longitude = models.CharField(max_length=10, null=True, blank=True)
#
#     loc = models.PointField(null=True, blank=True)
#
#     def __str__(self):
#         return f"{self.latitude}, {self.longitude}"
#
#     class Meta:
#         abstract = True
#
#
# class LocationsRadius(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_location_radius")
#
#     user_list = models.JSONField()
#
#     def __str__(self):
#         return self.user
#
#     class Meta:
#         abstract = True
