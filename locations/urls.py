from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("set", LocationViewSet, basename="user_location")

urlpatterns = [
                  path('update/', LocationViewSet.as_view(
                      {"patch": "update_location"}
                  ), name='user_set_location'),

              ] + router.urls
