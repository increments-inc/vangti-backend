from rest_framework import (
    permissions,
    response,
    status,
    views,
    viewsets,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import *
from .serializers import *
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

# CACHE_TTL = 60 * 15


@method_decorator(cache_page(60*1), name='dispatch')
class LocationViewSet(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "post"]

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    # @cache_page(CACHE_TTL)
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)


class ChatHistoryViewSet(viewsets.ModelViewSet):
    queryset = ChatHistory.objects.all()
    serializer_class = ChatHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]


class CallHistoryViewSet(viewsets.ModelViewSet):
    queryset = CallHistory.objects.all()
    serializer_class = CallHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get"]

