from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField

User = get_user_model()


class LocationUser(models.Model):
    user = models.CharField(max_length=256, null=True, blank=True)
    latitude = models.CharField(max_length=10, null=True, blank=True)
    longitude = models.CharField(max_length=10, null=True, blank=True)
    centre = models.PointField(null=True, blank=True)

    def __str__(self):
        return f"{self.latitude}, {self.longitude}"

    class Meta:
        ordering = ("centre",)


class LocationRadius(models.Model):
    location = models.OneToOneField(
        LocationUser, on_delete=models.CASCADE, related_name="location_radius_userlocation"
    )
    user_id_list = ArrayField(models.CharField(max_length=256))

    def __str__(self):
        return self.location.user

    class Meta:
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
