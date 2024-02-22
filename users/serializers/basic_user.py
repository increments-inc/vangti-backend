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
from rest_framework_simplejwt.tokens import Token, RefreshToken, AccessToken


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        for token in OutstandingToken.objects.filter(user=user):
            if not hasattr(token, 'blacklistedtoken'):
                print("hrhfg", token.token)
                BlacklistedToken.objects.create(token=token)
                print("blacklist", token)
            # toke = RefreshToken(token)
            # print(type(toke), toke.token_type)
        print(OutstandingToken.objects.all().count())
        token = super().get_token(user)
        print(OutstandingToken.objects.all().count())

        # Add custom claims
        token["is_active"] = user.is_active
        # token["is_to_be_deleted"] = user.user_delettion_schedule_user.is_to_be_deleted
        token["device"] = str(datetime.now())
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
        else:
            if not models.User.objects.filter(
                    phone_number=phone_number,
                    # user_info__device_token=device_id
            ).exists():
                return -2
        time_now = datetime.now()
        expires = time_now + timedelta(seconds=120)
        base_otp = pyotp.TOTP('base32secret3232').now()

        # default otp ---- for google, use a default phone condition
        if phone_number == settings.APP_STORE_DEFAULT_PHONE:
            base_otp = settings.APP_STORE_DEFAULT_OTP
        try:
            reg_phone = models.RegistrationOTPModel.objects.get(
                phone_number=phone_number,
                device_token=device_id
                # key=base_otp,
                # expires_at=expires
            )
            reg_phone.key = base_otp
            reg_phone.expires_at = expires
            reg_phone.save()
        except models.RegistrationOTPModel.DoesNotExist:
            reg_phone = models.RegistrationOTPModel.objects.create(
                phone_number=phone_number,
                device_token=device_id,
                key=base_otp,
                expires_at=expires
            )
        # host_user = settings.EMAIL_HOST_USER
        # insert sms service here
        # include this in celery
        if phone_number != settings.APP_STORE_DEFAULT_PHONE:
            response = requests.post(
                settings.SMS_URL,
                headers={
                    "Authorization": settings.SMS_API_KEY
                },
                json={
                    "sender_id": "8809617613332",
                    "receiver": f"{phone_number}",
                    "message": f"One Time Password (OTP) for Vangti App is {base_otp}",
                    "remove_duplicate": True
                }
            )
            print(response.json(), response.status_code)
        return reg_phone, base_otp

        # time_now = datetime.now()
        # expires = time_now + timedelta(seconds=310)
        # base_otp = pyotp.TOTP('base32secret3232').now()
        #
        # reg_phone = models.RegistrationOTPModel.objects.create(
        #     phone_number=phone_number,
        #     device_token=device_id,
        #     key=base_otp,
        #     expires_at=expires
        # )
        # host_user = settings.EMAIL_HOST_USER
        # # insert sms service here
        # # include this in celery
        # response = requests.post(
        #     settings.SMS_URL,
        #     headers={
        #         "Authorization": settings.SMS_API_KEY
        #     },
        #     json={
        #         "sender_id": "8809617613332",
        #         "receiver": f"{phone_number}",
        #         "message": f"One Time Password (OTP) for Vangti App is {base_otp}",
        #         "remove_duplicate": True
        #     }
        # )
        # print(response.json(), response.status_code)
        # return reg_phone, base_otp


class RegistrationSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(allow_null=True)
    phone_number = serializers.CharField()

    class Meta:
        model = models.User
        fields = ("phone_number", "otp",)

    # def validate(self, data):
    #     print("sdasda",data)
    #     if "phone_number" in data:
    #         data["phone_number"] = data["phone_number"]
    #
    #     return data

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number", None)
        otp = validated_data.pop("otp", None)
        time_now = datetime.now()
        reg = models.RegistrationOTPModel.objects.filter(
            phone_number=phone_number,
            expires_at__gte=time_now
        )
        if not reg.exists():
            return -1
        reg = reg.last()
        if str(reg.key) != otp:
            return -2

        try:
            user = models.User.objects.get(
                phone_number=phone_number
            )
            user.pin = None
            user.save()
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                phone_number=phone_number,
                pin=None
            )
        user.user_info.device_token = reg.device_token
        user.user_info.save()
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

        # pin can only be set once
        if user.pin is not None:
            return -2

        try:
            if user.pin is None:
                PINValidator().validate(password=pin)
                hasher = PBKDF2PasswordHasher()
                hashed_pin = hasher.encode(pin, settings.SALT)
                user.pin = hashed_pin
                user.save()
        except:
            return -1
        return user


#
# class UserPINResetSerializer(serializers.Serializer):
#     phone_number = serializers.CharField()
#     pin = serializers.CharField()
#
#     def create(self, validated_data):
#         phone_number = validated_data.pop("phone_number", None)
#         pin = validated_data.pop("pin", None)
#
#         try:
#             user = models.User.objects.get(
#                 phone_number=phone_number,
#             )
#         except:
#             return -1
#         """send message to user via otp"""
#         try:
#             PINValidator().validate(password=pin)
#             hasher = PBKDF2PasswordHasher()
#             hashed_pin = hasher.encode(pin, settings.SALT)
#             user.pin = hashed_pin
#             user.save()
#         except:
#             return -1
#         return user


class UserDeactivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("is_active", "pin")

    def update(self, instance, validated_data):
        user = self.context.get("request").user
        pin = validated_data.pop("pin", None)
        is_active = validated_data.pop("is_active", True)
        try:
            PINValidator().validate(password=pin)
        except:
            return -2
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
