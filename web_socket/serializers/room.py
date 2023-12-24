from django.urls import exceptions as url_exceptions
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers, validators
from rest_framework_simplejwt import settings as jwt_settings
from rest_framework_simplejwt import tokens
from rest_framework_simplejwt.exceptions import TokenError
from . import models
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from ..models import *
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance


class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = "__all__"


class CallHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CallHistory
        fields = "__all__"

