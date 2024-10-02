from rest_framework import exceptions, serializers, validators
from .. import models
from datetime import datetime, timedelta
import contextlib, json, random, pyotp, re
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Q
from django.urls import exceptions as url_exceptions
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers, validators
from rest_framework_simplejwt import tokens, settings as jwt_settings
from rest_framework_simplejwt.exceptions import TokenError
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from ..app_rest import TokenObtainPairSerializer
from .. import models
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from ..pin_validator import PINValidator
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
import requests
from django.utils.text import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from utils.log import logger


class UsersDeletionScheduleSerializer(serializers.ModelSerializer):
    # to_be_deleted = serializers.BooleanField(write_only=True, default=False)
    pin = serializers.CharField(write_only=True)

    class Meta:
        model = models.UsersDeletionSchedule
        fields = ("id", "pin",)
        read_only_fields = ["time_of_deletion", "user__phone_number"]

    def create(self, validated_data):
        logger.info(validated_data)
        pin = validated_data.pop("pin")
        # to_be_deleted = validated_data.pop("to_be_deleted")

        logger.info("sgdfhjgsdjh", pin)
        user = self.context.get('request').user
        user.is_active = False

        try:
            PINValidator().validate(password=pin)
        except:
            return -3
        hasher = PBKDF2PasswordHasher()
        hashed_pin = hasher.encode(pin, settings.SALT)
        if user.pin != hashed_pin:
            return -2
        try:

            schedule = models.UsersDeletionSchedule.objects.get(
                user=user
            )
        except:
            schedule = models.UsersDeletionSchedule.objects.create(
                user=user,
                time_of_deletion=datetime.now().date() + timedelta(days=30)
            )

        return schedule
