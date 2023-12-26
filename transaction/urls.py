from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("", TransactionViewSet, basename="transaction")
# router.register("user-mode", UserServiceModeViewSet, basename="user_service_mode")


urlpatterns = [
    path('change-mode/', UserServiceModeViewSet.as_view({"patch": "mode_change"}), name='user_mode_change'),

              ] + router.urls
