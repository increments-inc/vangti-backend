from django.contrib import admin
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# router.register("chat-history", ChatHistoryViewSet, basename="chat_history")
# router.register("call-history", CallHistoryViewSet, basename="call_history")

urlpatterns = [
        path('cancel-request/', CancelSearch.as_view()),
        # path('preferred-notes/', PreferredSearch.as_view()),
              ] + router.urls
