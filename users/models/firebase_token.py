from core.abstract_models import models, BaseModel
from .basic_user import User


class UserFirebaseToken(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_firebase_token"
    )
    firebase_token = models.CharField(max_length=512, null=True, blank=True)
    device_token = models.CharField(max_length=512, null=True, blank=True)

    class Meta:
        ordering = ("user",)

    def save(self, *args, **kwargs):
        if self._state.adding:
            print("new!", self.user)
            try:
                UserFirebaseToken.objects.filter(user=self.user).delete()
            except UserFirebaseToken.DoesNotExist:
                pass
        super().save(*args, **kwargs)
