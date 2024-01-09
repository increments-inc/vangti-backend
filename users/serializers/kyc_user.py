import contextlib, json, random, pyotp, re
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Q
from django.urls import exceptions as url_exceptions
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers, validators
from ..app_rest import TokenObtainPairSerializer
from .. import models
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from ..pin_validator import PINValidator
from django.contrib.auth.hashers import PBKDF2PasswordHasher


class AddNidSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserNidInformation
        fields = "__all__"
        read_only_fields = ("user", "user_photo", "signature",)

    def create(self, validated_data):
        user = self.context.get("request").user
        nid_front = validated_data.get("nid_front")
        nid_back = validated_data.get("nid_back")
        try:
            user_nid = models.UserNidInformation.objects.get(
                user=user
            )
            user_nid.nid_front = nid_front
            user_nid.nid_back = nid_back
            user_nid.save()
        except models.UserNidInformation.DoesNotExist:
            user_nid = models.UserNidInformation.objects.create(
                user=user,
                nid_front=nid_front,
                nid_back=nid_back
            )
        return user_nid


class AddKycSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserKYCInformation
        fields = "__all__"
        read_only_fields = ("user", "gender", "occupation", "acc_type",)

    def create(self, validated_data):
        user = self.context.get("request").user
        nid_no = validated_data.get("nid_no")
        name = validated_data.get("name")
        father_or_husband = validated_data.get("father_or_husband")
        mother = validated_data.get("mother")
        dob = validated_data.get("dob")
        present_address = validated_data.get("present_address")
        permanent_address = validated_data.get("permanent_address")
        try:
            user_nid = models.UserKYCInformation.objects.get(
                user=user
            )
            user_nid.nid_no = nid_no
            user_nid.name = name
            user_nid.father_or_husband = father_or_husband
            user_nid.mother = mother
            user_nid.dob = dob
            user_nid.present_address = present_address
            user_nid.permanent_address = permanent_address
            user_nid.save()
        except models.UserKYCInformation.DoesNotExist:
            user_nid = models.UserKYCInformation.objects.create(
                user=user,
                nid_no=nid_no,
                name=name,
                father_or_husband=father_or_husband,
                mother=mother,
                dob=dob,
                present_address=present_address,
                permanent_address=permanent_address,
            )
        return user_nid


class UpdateKycSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserKYCInformation
        fields = "__all__"
        read_only_fields = ["user"]
