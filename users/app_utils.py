from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .models import *
from django.contrib.auth.backends import BaseBackend
from datetime import datetime, timedelta

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
    def authenticate(request, username=None, otp=None):
        try:
            user = User.objects.get(
                Q(phone_number=username)
            )
        except User.DoesNotExist:
            return None

        userotp = user.user_otp.all().last()
        if str(otp) == str(userotp.key) and (userotp.expires_at >= datetime.now()):
            return user

        return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
