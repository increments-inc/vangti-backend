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

from django.utils.text import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["email"] = user.email
        token["is_superuser"] = user.is_superuser
        token["is_staff"] = user.is_staff
        return token


# use login
class NumberObtainPairSerializer(serializers.Serializer):
    phone = serializers.CharField()

    # class Meta:
    #     model = models.User
    #     fields = ("phone_number",)


class RegistrationOTPSerializer(serializers.ModelSerializer):
    is_reset_pin = serializers.BooleanField(default=False)

    class Meta:
        model = models.RegistrationOTPModel
        fields = ("phone_number", "device_token", "is_reset_pin",)

    def create(self, validated_data):
        print("here")
        phone_number = validated_data.pop("phone_number", None)
        device_id = validated_data.pop("device_token", None)
        is_reset_pin = validated_data.pop("is_reset_pin", False)

        if not is_reset_pin:
            if models.User.objects.filter(
                    phone_number=phone_number
            ).exists():
                return -1
            time_now = datetime.now()
            expires = time_now + timedelta(seconds=310)
            base_otp = pyotp.TOTP('base32secret3232').now()

            reg_phone = models.RegistrationOTPModel.objects.create(
                phone_number=phone_number,
                device_token=device_id,
                key=base_otp,
                expires_at=expires
            )
            host_user = settings.EMAIL_HOST_USER
            # insert sms service here
            # include this in celery
            send_mail(
                "Vangti OTP",
                f"Dear Customer,\nYour One-Time-Password for Vangti app is {base_otp}\nRegards,\nVangti Team",
                host_user,
                [host_user],
                fail_silently=False,
            )
            return reg_phone, base_otp
        else:
            if not models.User.objects.filter(
                    phone_number=phone_number
            ).exists():
                return -2
            time_now = datetime.now()
            expires = time_now + timedelta(seconds=310)
            base_otp = pyotp.TOTP('base32secret3232').now()

            reg_phone = models.RegistrationOTPModel.objects.create(
                phone_number=phone_number,
                device_token=device_id,
                key=base_otp,
                expires_at=expires
            )
            host_user = settings.EMAIL_HOST_USER
            # insert sms service here
            # include this in celery
            return reg_phone, base_otp


class RegistrationSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(allow_null=True)

    class Meta:
        model = models.User
        fields = ("phone_number", "otp",)

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number", None)
        otp = validated_data.pop("otp", None)
        time_now = datetime.now()
        try:
            reg = models.RegistrationOTPModel.objects.get(
                phone_number=phone_number,
                expires_at__gte=time_now
            )
            if str(reg.key) != otp:
                return -1
            user = models.User.objects.create(
                phone_number=phone_number,
                pin=None
            )
            user.user_info.device_token = reg.device_token
            user.user_info.save()

        except models.RegistrationOTPModel.DoesNotExist:
            return -1
        return user


class PINSerializer(serializers.ModelSerializer):
    new_pin = serializers.CharField()

    class Meta:
        model = models.User
        fields = ("pin", "new_pin")

    def update(self, instance, validated_data):
        new_pin = validated_data.pop("new_pin", None)
        pin = validated_data.pop("pin", None)

        hasher = PBKDF2PasswordHasher()
        hashed_pin = hasher.encode(pin, settings.SALT)

        if hashed_pin != instance.pin:
            return -1
        try:
            PINValidator().validate(password=new_pin)
            hasher = PBKDF2PasswordHasher()
            hashed_pin = hasher.encode(new_pin, settings.SALT)
            instance.pin = hashed_pin
            instance.save()
        except:
            return -1
        return instance


class UserPINSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    device_token = serializers.CharField()
    pin = serializers.CharField()

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number", None)
        pin = validated_data.pop("pin", None)
        device_token = validated_data.pop("device_token", None)
        print("device_id", device_token)
        try:
            user = models.User.objects.get(
                phone_number=phone_number,
                user_info__device_token=device_token
            )
            # user = models.UserInformation.objects.get(device_token=device_token).user
            print("user", user)
        except:
            return -1

        try:
            PINValidator().validate(password=pin)
            hasher = PBKDF2PasswordHasher()
            hashed_pin = hasher.encode(pin, settings.SALT)
            user.pin = hashed_pin
            user.save()
        except:
            return -1
        return user


#
class UserPINResetSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    pin = serializers.CharField()

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number", None)
        pin = validated_data.pop("pin", None)

        try:
            user = models.User.objects.get(
                phone_number=phone_number,
            )
        except:
            return -1
        """send message to user via otp"""
        try:
            PINValidator().validate(password=pin)
            hasher = PBKDF2PasswordHasher()
            hashed_pin = hasher.encode(pin, settings.SALT)
            user.pin = hashed_pin
            user.save()
        except:
            return -1
        return user


class UserDeactivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("is_active", "pin")

    def update(self, instance, validated_data):
        user = self.context.get("request").user
        pin = validated_data.pop("pin", None)
        is_active = validated_data.pop("is_active", True)
        PINValidator().validate(password=pin)
        hasher = PBKDF2PasswordHasher()
        hashed_pin = hasher.encode(pin, settings.SALT)
        print("23234234234234")
        if user.pin != hashed_pin:
            return -1
        user.is_active = is_active
        user.save()
        return user


# class UserInformationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.UserInformation
#         fields = ("person_name", "profile_pic", )


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.IntegerField()


class PhoneRegisterSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField()
    device_id = serializers.CharField(source="user_info.device_token", read_only=True)
    device_token = serializers.CharField(write_only=True)

    class Meta:
        model = models.User
        fields = ("id", "phone_number", "device_id", 'device_token',)
        read_only_fields = ["id", "device_id"]

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number", None)
        device_id = validated_data.pop("device_id", None)
        print(device_id)
        user = models.User.objects.create(
            phone_number=phone_number
        )
        # user.user_info.device_token =
        print(user)
        return user


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
