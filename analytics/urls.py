from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# router.register("", TransactionViewSet, basename="transaction")


urlpatterns = [
      path('home-analytics/', HomeAnalyticsViewSet.as_view({"get": "home_analytics"}),
           name='user_mode_change'),

] + router.urls
