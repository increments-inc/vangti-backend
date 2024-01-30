from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("app-feedback", AppFeedbackViewSet, basename="app_feedback")


urlpatterns = [
                  path('home-analytics/', HomeAnalyticsViewSet.as_view({"get": "home_analytics"}),
                       name='user_mode_change'),

                  path('profit/', InsightsViewSet.as_view({"get": "profit_by_time"}),
                       name='user_profit_by_time'),

                  path('transaction-avg/', InsightsViewSet.as_view({"get": "transaction_by_week"}),
                       name='user_transaction_by_week'),

                  path('demanded-vangti/', InsightsViewSet.as_view({"get": "most_vangti"}),
                       name='user_most_vangti'),

              ] + router.urls
