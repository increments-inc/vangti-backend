from rest_framework import exceptions, serializers, validators
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from .models import *
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from drf_extra_fields.geo_fields import PointField
from django.core.cache import cache
from django.db.models import Q


class LocationSerializer(serializers.ModelSerializer):
    google_api_data = serializers.SerializerMethodField()
    class Meta:
        model = UserLocation
        fields = (
            "latitude",
            "longitude",
            "user_phone_number",
            "centre",
            "google_api_data",
        )
        read_only_fields = ["user_phone_number","centre", "google_api_data"]
    def get_google_api_data(self, obj):
        return {
            "address":" dummy data",
            "address_long":" dummy data"
        }

    def user_list(self, obj):
        user = self.context.get("request").user

        center = obj.centre
        radius = 10000

        users = list(UserLocation.objects.exclude(user=user.id).filter(
            centre__distance_lte=(center, Distance(km=radius))
        ).values_list("user", flat=True))
        print(users)
        user_phone_list = User.objects.filter(id__in=users).values_list("phone_number", flat=True)
        try:
            print(user_phone_list)
            user_loc = LocationRadius.objects.get(
                location=obj
            )
            user_loc.user_id_list = list(user_phone_list)
            user_loc.save()
        except LocationRadius.DoesNotExist:
            LocationRadius.objects.create(
                location=obj,
                user_id_list=list(user_phone_list)
            )
        return

    def create(self, validated_data):
        user = self.context.get("request").user
        latitude = validated_data.pop("latitude", None)
        longitude = validated_data.pop("longitude", None)
        # loc = validated_data.pop("loc", None)
        loc_point = Point(float(longitude), float(latitude))

        user_location_point = UserLocation.objects.create(
            user=user.id,
            user_phone_number=user.phone_number,
            latitude=latitude,
            longitude=longitude,
            centre=loc_point
        )
        # self.user_list(user_location_point)
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
        # self.user_list(instance)
        return instance

# class LocationCacheSerializer(serializers.Serializer):
#     latitude = serializers.CharField()
#     longitude = serializers.CharField()
#
#     def to_representation(self, instance):
#         user = self.context.get("request").user
#         latitude = float(instance.get("latitude", None))
#         longitude = float(instance.get("longitude", None))
#
#         loc_point = Point(float(longitude), float(latitude))
#         cache.set(f"{user.id}", loc_point, timeout=None)
#         self.user_location()
#         return instance
#
#     def user_location(self):
#         user = self.context.get("request").user
#         user_center = cache.get(f"{user.id}")
#         user_id_list = User.objects.filter(~Q(id=user.id)).values_list("id", flat=True)
#         empty_dict_user_loc = {}
#         for userid in user_id_list:
#             user_loc = cache.get(f"{userid}")
#             if user_loc is not None:
#                 empty_dict_user_loc[userid] = user_loc
#         empty_users_list_for_cache = []
#         for user_no in empty_dict_user_loc:
#             user_location = empty_dict_user_loc[user_no]
#             dist = user_center.distance(user_location)
#             if dist <= settings.LOCATION_RADIUS:
#                 empty_users_list_for_cache.append(User.objects.get(id=user_no).phone_number)
#         cache.set(f"{user.phone_number}", empty_users_list_for_cache, timeout=None)
#         return
