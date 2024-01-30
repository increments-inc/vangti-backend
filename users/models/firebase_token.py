from core.abstract_models import models, BaseModel
from .basic_user import User


class UserFirebaseToken(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_firebase_token"
    )
    firebase_token = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        ordering = ("user",)
