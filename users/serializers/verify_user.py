from rest_framework import exceptions, serializers, validators
from .. import models
from drf_extra_fields.fields import Base64ImageField
from utils.helper import get_hash, get_original_hash
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample, extend_schema_field
from analytics.serializers import ProviderModeSerializer, SeekerModeSerializer, UserRating, UserSeekerRating
import os, random


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


class UpdateNidSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserNidInformation
        fields = "__all__"


class UserKYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserKYCDocument
        fields = ("file",)


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


class VerifiedUsersSerializer(serializers.ModelSerializer):
    is_submitted = serializers.BooleanField(default=False)

    class Meta:
        model = models.VerifiedUsers
        fields = ("is_submitted",)

    def create(self, validated_data):
        user = self.context.get("request").user
        is_submitted = validated_data.pop("is_submitted", False)
        nid_user = user.user_nid
        kyc_user = user.user_kyc
        if is_submitted:
            verified_user = models.VerifiedUsers.objects.create(
                user=user,
                nid_no=kyc_user.nid_no,
                name=kyc_user.name,
                father_or_husband=kyc_user.father_or_husband,
                mother=kyc_user.mother,
                dob=kyc_user.dob,
                present_address=kyc_user.present_address,
                permanent_address=kyc_user.permanent_address,
                phone_number=user.phone_number,
                user_photo=nid_user.user_photo,
                signature=nid_user.signature,
                gender=kyc_user.gender,
                occupation=kyc_user.occupation
            )
            # specify service mode enabling
            return verified_user
        return -1


class FrontNidSerializer(serializers.ModelSerializer):
    nid_front = serializers.ImageField()

    class Meta:
        model = models.UserNidInformation
        fields = ("nid_front",)


class BackNidSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserNidInformation
        fields = ("nid_back",)


class PhotoNidSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserNidInformation
        fields = ("user_photo",)


class SignNidSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserNidInformation
        fields = ("signature",)


@extend_schema_serializer(
    exclude_fields=('single',),  # schema ignore these fields
    examples=[
        OpenApiExample(
            'Example 1',
            value={
                "user_id": "string",
                "person_name": "string",
                "acc_type": "string",
                "profile_pic": {
                    "url": "string",
                    "hash": "string"
                },
                "phone_number": "string",
                "analytics_as_seeker": {
                    "rating": 0.0,
                    "total_deals_count": 0,
                    "transaction_amount": 0.0,
                    "deals_success_rate": 0.0,
                    "cancel_deals_count": 0
                },
                "analytics_as_provider": {
                    "rating": 0.0,
                    "total_deals_count": 0,
                    "transaction_amount": 0.0,
                    "deals_success_rate": 0.0,
                    "cancel_deals_count": 0
                },
                "is_provider": True,
            },
            response_only=True,  # signal that example only applies to responses
        ),
    ]
)
class UserInformationRetrieveSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    user_id = serializers.CharField(source="user.id", read_only=True)
    is_provider = serializers.BooleanField(source="user.user_mode.is_provider", read_only=True)
    profile_pic = Base64ImageField(required=False, allow_null=True)
    analytics_as_seeker = serializers.SerializerMethodField()
    analytics_as_provider = serializers.SerializerMethodField()

    class Meta:
        model = models.UserInformation
        fields = (
            "user_id",
            "person_name",
            "acc_type",
            "profile_pic",
            "phone_number",
            "analytics_as_seeker",
            "analytics_as_provider",

            "is_provider",

            # "transactions",
            # "deal_success_rate",
            # "total_amount",
            # "rating",
            # "cancelled_deals"
        )
        # exclude = ("user","device_id")
        read_only_fields = ("acc_type",)

    @extend_schema_field(SeekerModeSerializer)
    def get_analytics_as_seeker(self, obj):
        try:
            if getattr(obj.user, "seeker_rating_user", None) is None:
                instance = UserSeekerRating.objects.create(
                    user=obj.user
                )
                return SeekerModeSerializer(instance).data
            return SeekerModeSerializer(obj.user.seeker_rating_user).data
        except:
            return {
                "rating": 0.0,
                "total_deals_count": 0,
                "transaction_amount": 0.0,
                "deals_success_rate": 0.0,
                "cancel_deals_count": 0
            }

    @extend_schema_field(ProviderModeSerializer)
    def get_analytics_as_provider(self, obj):
        try:
            if getattr(obj.user, "userrating_user", None) is None:
                instance = UserRating.objects.create(
                    user=obj.user
                )
                return ProviderModeSerializer(instance).data
            return ProviderModeSerializer(obj.user.userrating_user).data
        except:
            return {
                "rating": 0.0,
                "total_deals_count": 0,
                "transaction_amount": 0.0,
                "deals_success_rate": 0.0,
                "cancel_deals_count": 0
            }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')

        if rep.get('is_provider') is None:
            rep['is_provider'] = False

        rep['profile_pic'] = {
            "url": None,
            "hash": None
        }

        if instance.profile_pic:
            try:
                image = request.build_absolute_uri(instance.profile_pic.url)
                url_hash = instance.profile_pic_hash
            except:
                image = None
                url_hash = None
            rep['profile_pic'] = {
                "url": image,
                "hash": url_hash
            }
        else:
            # serving default images
            file_path = f"/media/avatars/{random.randrange(1, 9)}.png"
            if os.path.exists(f"{os.path.abspath(os.getcwd())}{file_path}"):
                rep['profile_pic'] = {
                    "url": request.build_absolute_uri(file_path),
                    "hash": "LsOg6a-S?+S_]}kAtPNI7dbZm?r]"
                }

        return rep
