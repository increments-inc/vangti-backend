from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("rate-as-seeker", TransactionAsSeekerReviewViewSet, basename="transaction_rate_as_seeker")

router.register("rate-as-provider", TransactionAsProviderReviewViewSet, basename="transaction_rate_as_provider")

router.register(
    "report-abuse-as-seeker", TransactionAsSeekerAbuseReportViewSet, basename="transaction_report_abuse_as_seeker"
)

router.register(
    "report-abuse-as-provider", TransactionAsProviderAbuseReportViewSet, basename="transaction_report_abuse_as_provider"
)


# router.register("search-vangti", TransactionRequestViewSet, basename="transaction_request")
router.register("messages", TransactionMessagesViewSet, basename="transaction_messages")
router.register("", TransactionViewSet, basename="transaction")


urlpatterns = [
                  # path('update-by-provider/', TransactionViewSet.as_view({"patch": "update_provider"}),
                  #      name='user_update_provider'),
                  path('update-by-seeker/', TransactionViewSet.as_view({"patch": "update_seeker"}),
                       name='user_update_seeker'),


                # user service mode
                  path('get-user-mode/', UserServiceModeViewSet.as_view({"get": "get_mode"}),
                       name='user_get_mode'),
                  path('change-user-mode/', UserServiceModeViewSet.as_view({"patch": "mode_change"}),
                       name='user_mode_change'),


                  path('history/provider/', TransactionHistoryViewSet.as_view({"get": "provider_history"}),
                       name='provider_history'),
                  path('history/seeker/', TransactionHistoryViewSet.as_view({"get": "seeker_history"}),
                       name='seeker_history'),

                  # rating
                  # path('rate-deal-as-seeker/', TransactionRatingViewSet.as_view({"post": "create"}),
                  #      name='transaction_as_seeker_review'),
                  #
                  # # rating
                  # path('rate-deal-as-provider/', TransactionRatingViewSet.as_view({"post": "create"}),
                  #      name='transaction_as_provider_review'),

                  # transaction open
                  path('open-deals/', TransactionViewSet.as_view({"get": "open_transactions"}),
                       name='user_open_transactions'),
              ] + router.urls
