from rest_framework import exceptions, serializers, validators
from .. import models


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


class UserInformationRetrieveSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    # rating = serializers.FloatField(source="user.rating")
    class Meta:
        model = models.UserInformation
        fields = (
            "person_name",
            "acc_type",
            "profile_pic",
            "phone_number",
            # "rating"
        )
        # exclude = ("user","device_id")
        read_only_fields = ("acc_type",)

