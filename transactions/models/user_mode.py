from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel

User = get_user_model()


class UserServiceMode(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_mode"
    )
    is_provider = models.BooleanField(default=False)

    class Meta:
        ordering = ("user",)

