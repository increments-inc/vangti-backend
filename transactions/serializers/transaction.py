from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from ..models import *
import blurhash
from locations.models import UserLocation
from django.contrib.gis.db.models.functions import Distance


def get_hash(picture_url):
    with open(picture_url[1:], 'rb') as image_file:
        hash = blurhash.encode(image_file, x_components=4, y_components=3)
    return hash


class HashPictureSerializer(serializers.Serializer):
    url = serializers.CharField()
    hash = serializers.CharField()


class InfoSerializer(serializers.Serializer):
    picture = HashPictureSerializer()
    name = serializers.CharField()
    rating = serializers.FloatField()
    deals = serializers.IntegerField()
    deal_amounts = serializers.FloatField()
    dislikes = serializers.IntegerField()
    deal_success_rate = serializers.FloatField()
    distance = serializers.CharField()
    phone_number = serializers.CharField()


class TransactionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionHistory
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):
    transaction_no = serializers.SerializerMethodField()
    seeker_info = serializers.SerializerMethodField()
    provider_info = serializers.SerializerMethodField()
    qr = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        # fields = "__all__"
        exclude = ("id","qr_image",)

    @staticmethod
    def get_transaction_no(obj):
        number = obj.get_transaction_unique_no
        return number

    @extend_schema_field(HashPictureSerializer)
    def get_qr(self, obj):
        request = self.context.get('request')
        try:
            image = request.build_absolute_uri(obj.qr_image.url)
            hash = get_hash(obj.qr_image.url)
        except:
            image = ""
            hash = ""

        return {
            "url": image,
            "hash": hash
        }

    @extend_schema_field(InfoSerializer)
    def get_seeker_info(self, obj):
        request = self.context.get('request')

        name = obj.seeker.user_info.person_name
        picture = obj.seeker.user_info.profile_pic
        try:
            url = request.build_absolute_uri(picture.url)
            hash = get_hash(picture.url)
        except:
            url = ""
            hash = ""
        rating = obj.seeker.userrating_user.rating
        deals = obj.seeker.userrating_user.no_of_transaction
        deal_amounts = obj.seeker.userrating_user.total_amount_of_transaction
        dislikes = obj.seeker.userrating_user.dislikes
        deal_success_rate = obj.seeker.userrating_user.deal_success_rate

        distance = str(0)
        phone_number = obj.seeker.phone_number
        return {
            "name": name,
            "picture": {
                "url": url,
                "hash": hash
            },
            "rating": rating,
            "deals": deals,
            "amount": deal_amounts,
            "dislikes": dislikes,
            "deal_success_rate": deal_success_rate,
            "distance": distance,
            "phone_number": phone_number
        }

    @extend_schema_field(InfoSerializer)
    def get_provider_info(self, obj):
        request = self.context.get('request')

        name = obj.provider.user_info.person_name
        picture = obj.provider.user_info.profile_pic
        try:
            url = request.build_absolute_uri(picture.url)
            hash = get_hash(picture.url)
        except:
            url = ""
            hash = ""
        rating = obj.provider.userrating_user.rating
        deals = obj.provider.userrating_user.no_of_transaction
        deal_amounts = obj.provider.userrating_user.total_amount_of_transaction
        dislikes = obj.provider.userrating_user.dislikes
        deal_success_rate = obj.provider.userrating_user.deal_success_rate
        distance = str(0)
        phone_number = obj.provider.phone_number
        return {
            "name": name,
            "picture": {
                "url": url,
                "hash": hash
            },
            "rating": rating,
            "deals": deals,
            "amount": deal_amounts,
            "dislikes": dislikes,
            "deal_success_rate": deal_success_rate,
            "distance": distance,
            "phone_number": phone_number
        }


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

    def get_distance(self, obj):
        user = self.context.get("request").user
        user_center = UserLocation.objects.get(user=user.id).centre
        provider_id = obj.provider.id
        provider = UserLocation.objects.get(user=obj.provider.id)

        distance = 100

        all_distance = dict(UserLocation.objects.filter(user=user.id).annotate(
            distance=Distance("centre", provider.centre)).values("user_phone_number", "distance"))
        print(all_distance, "all distance all")

        return f"{distance}"

    @extend_schema_field(HashPictureSerializer)
    def get_provider_picture(self, obj):
        request = self.context.get("request")
        hash = ""
        provider_pic = obj.provider.user_info.profile_pic
        if provider_pic is not None:
            with open(provider_pic.url[1:], 'rb') as image_file:
                hash = blurhash.encode(image_file, x_components=4, y_components=3)
        else:
            hash = ""
        return {
            "url": request.build_absolute_uri(provider_pic.url),
            "hash": hash
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
        if ret["provider_picture"] is None:
            ret['provider_picture'] = ""
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
        hash = ""
        seeker_pic = obj.seeker.user_info.profile_pic
        if seeker_pic is not None:
            with open(seeker_pic.url[1:], 'rb') as image_file:
                hash = blurhash.encode(image_file, x_components=4, y_components=3)
        else:
            hash = ""
        return {
            "url": request.build_absolute_uri(seeker_pic.url),
            "hash": hash
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret["total_deals"] is None:
            ret['total_deals'] = 0
        if ret["rating"] is None:
            ret['rating'] = float(0)
        if ret["seeker_picture"] is None:
            ret['seeker_picture'] = ""
        return ret
