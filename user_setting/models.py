from core.abstract_models import models, BaseModel
from utils.helper import content_file_path, ImageCompress
from django.contrib.auth import get_user_model
User = get_user_model()


class UserSetting(BaseModel):
    LANG = [
        ("ENGLISH", "English"),
        ("BANGLA", "Bangla"),

    ]
    language = models.CharField(max_length=10, choices=LANG, default="ENGLISH")
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_setting"
    )
    accepted_terms = models.BooleanField(default=False)
    accepted_timestamp = models.DateTimeField()

    class Meta:
        ordering = ["user"]


class VangtiTerms(BaseModel):
    terms_and_conditions = models.FileField(upload_to=content_file_path, null=True, blank=True)
    privacy_policy = models.FileField(upload_to=content_file_path, null=True, blank=True)
    about = models.FileField(upload_to=content_file_path, null=True, blank=True)

    def __str__(self):
        return "vangti terms"