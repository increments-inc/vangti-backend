from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .models import *
from django.contrib.auth.backends import BaseBackend
from datetime import datetime, timedelta
from .pin_validator import PINValidator
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.conf import settings
User = get_user_model()


class RegAccessToken(AccessToken):
    lifetime = timedelta(minutes=10)


def get_reg_token(user):
    reg_access = RegAccessToken.for_user(user)
    return str(reg_access)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class EmailPhoneUsernameAuthentication(BaseBackend):
    @staticmethod
    def authenticate(request, username=None, pin=None):
        try:
            user = User.objects.get(
                Q(phone_number=username)
            )
        except User.DoesNotExist:
            return None

        # userotp = user.user_otp.all().last()
        # if str(pin) == str(userotp.key) and (userotp.expires_at >= datetime.now()):
        #     return user


        # try:
        # PINValidator().validate(password=pin)

        hasher = PBKDF2PasswordHasher()
        hashed_pin = hasher.encode(pin, settings.SALT)

        if hashed_pin == user.pin:
            return user



        return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
