from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register("set", LocationViewSet, basename="user_location")

urlpatterns = [
                  path('get/', LocationViewSet.as_view(
                      {"get": "get_location"}
                  ), name='user_set_location'),
                  # path('set/', LocationViewSet.as_view(
                  #     {"post": "post_location"}
                  # ), name='user_set_location'),
                  path('update/', LocationViewSet.as_view(
                      {"patch": "update_location"}
                  ), name='user_set_location'),

              ] + router.urls
