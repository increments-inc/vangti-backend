from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from ..models import *
from locations.models import UserLocation
from django.contrib.gis.db.models.functions import Distance
from utils.helper import get_hash
from users.serializers import UserInformationRetrieveSerializer

class HashPictureSerializer(serializers.Serializer):
    url = serializers.CharField(allow_null=True)
    hash = serializers.CharField(allow_null=True)


class InfoSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    person_name = serializers.CharField()

    acc_type = serializers.CharField()
    profile_pic = HashPictureSerializer()

    phone_number = serializers.CharField()
    transactions = serializers.IntegerField()
    is_provider = serializers.BooleanField()
    deal_success_rate = serializers.FloatField()
    total_amount = serializers.FloatField()


    rating = serializers.FloatField()
    cancelled_deals = serializers.IntegerField()



class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    transaction_no = serializers.SerializerMethodField()
    seeker_info = serializers.SerializerMethodField()
    provider_info = serializers.SerializerMethodField()
    qr = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        # fields = "__all__"
        exclude = ("id", "qr_image","qr_image_hash",)

    @extend_schema_field(serializers.CharField)
    def get_distance(self,obj):
        # seeker_point = UserLocation.objects.get(user = obj.seeker.id)
        provider_point = UserLocation.objects.get(user = obj.provider.id).centre

        all_distance = (
            UserLocation.objects.filter(user=obj.seeker.id).annotate(
                distance=Distance("centre", provider_point)
            ).values("distance").first()["distance"].m
        )
        return f"{int(all_distance)}"

    @staticmethod
    def get_transaction_no(obj):
        number = obj.get_transaction_unique_no
        return number

    @extend_schema_field(HashPictureSerializer)
    def get_qr(self, obj):
        request = self.context.get('request')
        try:
            image = request.build_absolute_uri(obj.qr_image.url)
            url_hash = obj.qr_image_hash
        except:
            image = None
            url_hash = None

        return {
            "url": image,
            "hash": url_hash
        }
    @extend_schema_field(UserInformationRetrieveSerializer)
    def get_seeker_info(self, obj):
        return UserInformationRetrieveSerializer(obj.seeker.user_info, context={"request": self.context.get('request')}).data

    @extend_schema_field(UserInformationRetrieveSerializer)
    def get_provider_info(self, obj):
        return UserInformationRetrieveSerializer(obj.provider.user_info, context={"request": self.context.get('request')}).data


class TransactionProviderSerializer(serializers.ModelSerializer):
    transaction_no = serializers.CharField(source="get_transaction_unique_no")

    class Meta:
        model = Transaction
        fields = (
            "transaction_no",
            "is_completed",
        )
        read_only_fields = ("is_completed",)

    def update(self, instance, validated_data):
        instance.is_completed = True
        instance.save()
        return instance


class TransactionSeekerSerializer(serializers.ModelSerializer):
    transaction_no = serializers.CharField(source="get_transaction_unique_no")

    class Meta:
        model = Transaction
        fields = (
            "transaction_no",
            "transaction_pin",
            "is_completed",
        )
        read_only_fields = ("is_completed",)

    def update(self, instance, validated_data):
        pin = validated_data.pop("transaction_pin", None)
        if pin == instance.transaction_pin:
            instance.is_completed = True
            instance.save()
            return instance
        return -1


class TransactionSeekerHistorySerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source="provider.user_info.person_name", read_only=True)
    total_amount__of_transactions = serializers.FloatField(source="provider.userrating_user.no_of_transaction",
                                                           read_only=True)
    rating = serializers.FloatField(source="provider.userrating_user.rating", read_only=True)
    dislikes = serializers.IntegerField(source="provider.userrating_user.dislikes", read_only=True)
    deal_success_rate = serializers.FloatField(source="provider.userrating_user.deal_success_rate", read_only=True)
    distance = serializers.SerializerMethodField(read_only=True)
    provider_picture = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TransactionHistory
        fields = (
            "id",
            "total_amount",
            "preferred_notes",
            "created_at",

            "provider_name",
            "total_amount__of_transactions",
            "rating",
            "dislikes",
            "deal_success_rate",
            "distance",
            "provider_picture",
        )

    # user distance revise !!
    def get_distance(self, obj):
        user = self.context.get("request").user
        provider = UserLocation.objects.get(user=obj.provider.id)
        all_distance = (
            UserLocation.objects.filter(user=user.id).annotate(
                distance=Distance("centre", provider.centre)
            ).values("distance").first()["distance"].km
        )
        return f"{int(all_distance)}"

    @extend_schema_field(HashPictureSerializer)
    def get_provider_picture(self, obj):
        request = self.context.get("request")
        try:
            provider_pic = obj.provider.user_info.profile_pic
            url = request.build_absolute_uri(provider_pic.url)
            url_hash = obj.provider.user_info.profile_pic_hash
        except:
            url = None
            url_hash = None

        return {
            "url": url,
            "hash": url_hash
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret["total_amount__of_transactions"] is None:
            ret['total_amount__of_transactions'] = float(0)
        if ret["rating"] is None:
            ret['rating'] = float(0)
        if ret["dislikes"] is None:
            ret['dislikes'] = 0
        if ret["deal_success_rate"] is None:
            ret['deal_success_rate'] = float(0)
        # if ret["provider_picture"] is None:
        #     ret['provider_picture'] = ""
        return ret


class TransactionProviderHistorySerializer(serializers.ModelSerializer):
    seeker_name = serializers.CharField(source="seeker.user_info.person_name", read_only=True)
    total_deals = serializers.IntegerField(source="seeker.userrating_user.no_of_transaction", read_only=True)
    rating = serializers.FloatField(source="seeker.userrating_user.rating", read_only=True)
    seeker_picture = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TransactionHistory
        fields = (
            "id",
            "total_amount",
            "preferred_notes",
            "created_at",
            "seeker_name",
            "total_deals",
            "rating",
            "seeker_picture",
        )

    @extend_schema_field(HashPictureSerializer)
    def get_seeker_picture(self, obj):
        request = self.context.get("request")
        try:
            seeker_pic = obj.seeker.user_info.profile_pic
            url = request.build_absolute_uri(seeker_pic.url)
            url_hash = obj.seeker.user_info.profile_pic_hash
        except:
            url = None
            url_hash = None

        return {
            "url": url,
            "hash": url_hash
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret["total_deals"] is None:
            ret['total_deals'] = 0
        if ret["rating"] is None:
            ret['rating'] = float(0)
        # if ret["seeker_picture"] is None:
        #     ret['seeker_picture'] = ""
        return ret
