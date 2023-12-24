from django.urls import exceptions as url_exceptions
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers, validators
from rest_framework_simplejwt import settings as jwt_settings
from rest_framework_simplejwt import tokens
from rest_framework_simplejwt.exceptions import TokenError
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from ..models import *
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLocation
        fields = "__all__"
        read_only_fields = ["user", "loc"]

    def create(self, validated_data):
        user = self.context.get("request").user
        latitude = float(validated_data.pop("latitude", None))
        longitude = float(validated_data.pop("longitude", None))
        # loc = validated_data.pop("loc", None)

        loc = Point(longitude, latitude)

        user_location_point = UserLocation.objects.create(
            user=user,
            latitude=latitude,
            longitude=longitude,
            loc=loc
        )
        get_user_list(user)
        return user_location_point

    def update(self, instance, validated_data):
        user = self.context.get("request").user
        latitude = float(validated_data.pop("latitude", None))
        longitude = float(validated_data.pop("longitude", None))

        loc = Point(longitude, latitude)

        instance.latitude = latitude
        instance.longitude = longitude
        instance.loc = loc
        instance.save()
        get_user_list(user)
        return instance


def get_user_list(user):
    center = user.user_location.loc
    radius = 10000

    users = list(UserLocation.objects.exclude(user__id=user.id).filter(
        loc__distance_lte=(center, Distance(km=radius))
    ).values_list("user__phone_number", flat=True))
    LocationRadius.objects.create(
        user_location=user.user_location,
        user_list={"users": users}
    )
    return
