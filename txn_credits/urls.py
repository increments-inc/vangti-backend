from django.urls import path, include
from .views import AccumulatedCreditsViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("", AccumulatedCreditsViewSet, basename="user_credits")

urlpatterns = [

] + router.urls
