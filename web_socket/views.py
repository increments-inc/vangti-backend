from django.http import JsonResponse
from rest_framework import (
    permissions,
    response,
    status,
    views,
    viewsets,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import *
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from rest_framework.decorators import api_view, schema
from rest_framework.views import APIView
from django.conf import settings
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from core.celery import app
# from celery.decorators import task
from django.contrib.auth import authenticate, login

def vangti_request(request):
    message = {
        "seeker": "ajk",
    }
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "14-location-room", {
            'type': 'send_sdpt',
            'receive_dict': message,
        },
        # immediately=True
    )
    return JsonResponse({"message": message})



