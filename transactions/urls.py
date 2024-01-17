from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register("search-vangti", TransactionRequestViewSet, basename="transaction_request")
router.register("", TransactionViewSet, basename="transaction")
# router.register("user-mode", UserServiceModeViewSet, basename="user_service_mode")

urlpatterns = [
                  path('get-user-mode/', UserServiceModeViewSet.as_view({"get": "get_mode"}),
                       name='user_get_mode'),
                  path('change-user-mode/', UserServiceModeViewSet.as_view({"patch": "mode_change"}),
                       name='user_mode_change'),


                  path('history/provider/', TransactionHistoryViewSet.as_view({"get": "provider_history"}),
                       name='provider_history'),
                  path('history/seeker/', TransactionHistoryViewSet.as_view({"get": "seeker_history"}),
                       name='seeker_history'),

                  # rating
                  path('rate-deal/', TransactionRatingViewSet.as_view({"post": "rate_transaction"}),
                       name='transaction_get_review'),

                  # transaction requests

                  # path('search-vangti/', VangtiSearch.as_view(),
                  #      name='transaction_search_vangti'),
              ] + router.urls
