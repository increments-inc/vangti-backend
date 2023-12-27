from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("", TransactionViewSet, basename="transaction")
# router.register("user-mode", UserServiceModeViewSet, basename="user_service_mode")
router.register("history", TransactionHistoryViewSet, basename="transaction_history")

urlpatterns = [
      path('change-mode/', UserServiceModeViewSet.as_view({"patch": "mode_change"}),
           name='user_mode_change'),

      path('history/provider/', TransactionHistoryViewSet.as_view({"get": "provider_history"}),
           name='provider_history'),
      path('history/seeker/', TransactionHistoryViewSet.as_view({"get": "seeker_history"}),
           name='seeker_history'),

] + router.urls
