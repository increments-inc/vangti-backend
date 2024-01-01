from core.abstract_models import models, BaseModel
from django.contrib.auth.models import BaseUserManager
from utils.helper import content_file_path, ImageCompress
from .basic_info import User

GENDER = [
    ("MALE", "Male"),
    ("FEMALE", "Female"),
    ("OTHER", "Other"),
]
OCCUPATION = [
    ("EMPLOYEE", "Employee"),
    ("BUSINESS", "Business"),
    ("STUDENT", "Student"),
    ("HOUSE_WIFE", "House Wife"),
    ("OTHER", "Other"),
]
ACCOUNT_TYPE = [
    ("PERSONAL", "Personal"),
    ("BUSINESS", "Business"),
]


class UserInformation(BaseModel):
    """
    Model to store user basic information
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_info"
    )
    device_id = models.CharField(max_length=512, null=True, blank=True)
    person_name = models.CharField(max_length=255, null=True, blank=True)
    acc_type = models.CharField(max_length=25, choices=ACCOUNT_TYPE, default="PERSONAL")
    profile_pic = models.ImageField(upload_to=content_file_path, blank=True, null=True)
    __original_image = None

    def __str__(self):
        return f"{self.user}'s information"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_image = self.profile_pic

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.profile_pic != self.__original_image:
            self.profile_pic = ImageCompress(self.profile_pic)

        super().save(force_insert, force_update, *args, **kwargs)
        self.__original_image = self.profile_pic


class UserNidInformation(BaseModel):
    """
    Model to store user nid information
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_nid"
    )

    user_photo = models.ImageField(upload_to=content_file_path, blank=True, null=True)
    nid_front = models.ImageField(upload_to=content_file_path, blank=True, null=True)
    nid_back = models.ImageField(upload_to=content_file_path, blank=True, null=True)
    signature = models.ImageField(upload_to=content_file_path, blank=True, null=True)

    # is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}'s nid information"


class UserKYCInformation(BaseModel):
    """
    Model to store user kyc information
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_kyc"
    )
    nid_no = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    father_or_husband = models.CharField(max_length=255, null=True, blank=True)
    mother = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField()
    present_address = models.CharField(max_length=254, blank=True)
    permanent_address = models.CharField(max_length=254, blank=True)

    gender = models.CharField(max_length=15, choices=GENDER, null=True, blank=True)
    occupation = models.CharField(max_length=25, choices=OCCUPATION, null=True, blank=True)
    acc_type = models.CharField(max_length=25, choices=ACCOUNT_TYPE, null=True, blank=True)

    def __str__(self):
        return f"{self.user}'s KYC information"


class UserKYCDocument(BaseModel):
    """
    Model to store user documents
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_document"
    )
    file = models.FileField()

    def __str__(self):
        return f"{self.user}'s file"


class VerifiedUsers(BaseModel):
    """
    Model to store verified users
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="users_verified"
    )
    nid_no = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    father_or_husband = models.CharField(max_length=255, null=True, blank=True)
    mother = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField()
    present_address = models.CharField(max_length=254, blank=True)
    permanent_address = models.CharField(max_length=254, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    user_photo = models.ImageField(upload_to=content_file_path, blank=True, null=True)
    signature = models.ImageField(upload_to=content_file_path, blank=True, null=True)
    gender = models.CharField(max_length=15, null=True, blank=True)
    occupation = models.CharField(max_length=25, null=True, blank=True)

    def __str__(self):
        return f"{self.user} verified"
