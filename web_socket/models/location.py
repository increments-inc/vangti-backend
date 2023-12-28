from django.contrib.gis.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserLocation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_location")
    latitude = models.CharField(max_length=10, null=True, blank=True)
    longitude = models.CharField(max_length=10, null=True, blank=True)

    loc = models.PointField(null=True, blank=True)

    def __str__(self):
        return f"{self.latitude}, {self.longitude}"

    class Meta:
        abstract = True


class LocationRadius(models.Model):
    # user_location = models.ForeignKey(UserLocation, on_delete=models.CASCADE, related_name="user_location_radius")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_location_radius")

    user_list = models.JSONField()

    def __str__(self):
        return self.user

    class Meta:
        abstract = True