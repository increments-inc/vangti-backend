import contextlib, json, random, pyotp, re
from django.contrib.auth import authenticate, login, get_user_model
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
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.core.validators import RegexValidator
from django.utils import timezone
import firebase_admin
from firebase_admin import auth, credentials
from django.core.exceptions import ValidationError


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    phone_number = serializers.CharField(required=True)
    firebase_token = serializers.CharField(required=True)
    device_token = serializers.CharField(required=False)

    def validate(self, attrs):
        try:
            # Verify Firebase token
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
                firebase_admin.initialize_app(cred)

            decoded_token = auth.verify_id_token(attrs['firebase_token'])
            phone_number = decoded_token.get('phone_number')

            if phone_number != attrs['phone_number']:
                raise serializers.ValidationError("Phone number mismatch")

            # Get or create user
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                user = User.objects.create(phone_number=phone_number)
                models.UserInformation.objects.create(user=user)

            # Update device token if provided
            if attrs.get('device_token'):
                user.user_info.device_token = attrs['device_token']
                user.user_info.save()

            # Generate token
            refresh = self.get_token(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'is_active': user.is_active,
                'device': str(datetime.now())
            }
            return data

        except Exception as e:
            raise serializers.ValidationError(str(e))

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["is_active"] = user.is_active
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
                # device_token=device_id
            )
            reg_phone.key = base_otp
            reg_phone.expires_at = expires
            reg_phone.is_reset = is_reset_pin
            reg_phone.save()
        except models.RegistrationOTPModel.DoesNotExist:
            reg_phone = models.RegistrationOTPModel.objects.create(
                phone_number=phone_number,
                device_token=device_id,
                key=base_otp,
                expires_at=expires,
                is_reset=is_reset_pin
            )
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
        # logger.info(response.json(), response.status_code)
        # return reg_phone, base_otp


class RegistrationOTPVerifySerializer(serializers.ModelSerializer):
    otp = serializers.CharField(source="key")

    class Meta:
        model = models.RegistrationOTPModel
        fields = ("phone_number", "otp",)

    def update(self, instance, validated_data):
        otp = validated_data.get("key", None)
        if otp != instance.key:
            return -1
        instance.is_active = True
        instance.save()
        return instance


User = get_user_model()

class FirebasePhoneAuthSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    firebase_token = serializers.CharField(max_length=1000)
    device_token = serializers.CharField(required=False)

    def validate(self, data):
        try:
            # Initialize Firebase Admin SDK if not already initialized
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
                firebase_admin.initialize_app(cred)

            # Verify the Firebase token
            decoded_token = auth.verify_id_token(data['firebase_token'])
            phone_number = decoded_token.get('phone_number')

            if phone_number != data['phone_number']:
                raise serializers.ValidationError("Phone number mismatch")

            return data
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        device_token = validated_data.get('device_token')
        
        try:
            user = User.objects.get(phone_number=phone_number)
            # Update device token if provided
            if device_token:
                user.user_info.device_token = device_token
                user.user_info.save()
        except User.DoesNotExist:
            user = User.objects.create(phone_number=phone_number)
            # Create user info with device token if provided
            if device_token:
                models.UserInformation.objects.create(user=user, device_token=device_token)
            else:
                models.UserInformation.objects.create(user=user)
        return user


class RegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=15)
    firebase_token = serializers.CharField(max_length=1000, required=True)
    pin = serializers.CharField(required=True)
    device_token = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('phone_number', 'pin', 'firebase_token', 'device_token')

    def validate(self, attrs):
        # Verify Firebase token
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
                firebase_admin.initialize_app(cred)

            decoded_token = auth.verify_id_token(attrs['firebase_token'])
            phone_number = decoded_token.get('phone_number')

            if phone_number != attrs['phone_number']:
                raise serializers.ValidationError({"phone_number": "Phone number mismatch"})
        except Exception as e:
            raise serializers.ValidationError({"firebase_token": str(e)})

        # Validate PIN
        try:
            PINValidator().validate(password=attrs['pin'])
        except ValidationError as e:
            raise serializers.ValidationError({"pin": str(e)})

        return attrs

    def create(self, validated_data):
        phone_number = validated_data.pop('phone_number')
        pin = validated_data.pop('pin')
        device_token = validated_data.pop('device_token', None)
        validated_data.pop('firebase_token')

        # Create user
        user = User.objects.create(phone_number=phone_number)
        
        # Set PIN
        hasher = PBKDF2PasswordHasher()
        hashed_pin = hasher.encode(pin, settings.SALT)
        user.pin = hashed_pin
        user.save()

        # Create user info with device token
        if device_token:
            models.UserInformation.objects.create(user=user, device_token=device_token)
        else:
            models.UserInformation.objects.create(user=user)

        return user


class PINSerializer(serializers.ModelSerializer):
    new_pin = serializers.CharField()

    class Meta:
        model = get_user_model()
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
        try:
            user = get_user_model().objects.get(
                phone_number=phone_number,
                user_info__device_token=device_token
            )
            # user = models.UserInformation.objects.get(device_token=device_token).user
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
        model = get_user_model()
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
        if instance.pin != hashed_pin:
            return -1
        instance.is_active = is_active
        instance.save()

        return instance


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
        model = get_user_model()
        fields = ("id", "phone_number", "device_id", 'device_token',)
        read_only_fields = ["id", "device_id"]

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number", None)
        device_id = validated_data.pop("device_id", None)
        user = get_user_model().objects.create(
            phone_number=phone_number
        )
        # user.user_info.device_token =
        return user


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
