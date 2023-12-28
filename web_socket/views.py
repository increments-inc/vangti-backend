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
from django.core.cache import cache
from rest_framework.decorators import api_view, schema
from rest_framework.views import APIView


# CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
# CACHE_TTL = 60 * 15


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


# @method_decorator(cache_page(60*1), name='dispatch')
# class LocationViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = LocationSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     http_method_names = ["get", "patch", "post"]
#
#     def get_serializer_class(self):
#         if self.action == "set_location":
#             return LocationCacheSerializer
#         return self.serializer_class
#
#     def perform_create(self, serializer):
#         return serializer.save(user=self.request.user)

class SetUserLocation(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationCacheSerializer

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data, context={"request": self.request})
        if serializer.is_valid():
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
