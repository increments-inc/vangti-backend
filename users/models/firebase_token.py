from core.abstract_models import models, BaseModel
from .basic_info import User


class UserFirebaseToken(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_firebase_token"
    )
    firebase_token = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        ordering = ("user",)
