# from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from core.abstract_models import models, BaseModel
from django.core.validators import RegexValidator

User = get_user_model()


class SubscriptionPackage(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True


class Subscription(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscription_user"
    )
    package = models.ForeignKey(
        SubscriptionPackage, on_delete=models.CASCADE, related_name="subscription_package"
    )

    class Meta:
        abstract = True


class Referrals(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscription_user"
    )

    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+880XXXX-XXXXXX'. Up to 13 "
                                         "digits allowed.")
    friend = models.CharField(validators=[phone_regex], max_length=15, unique=True)

    class Meta:
        abstract = True


class UserPoints(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="userpoints_user"
    )
    points = models.IntegerField(default=0)

    class Meta:
        abstract = True
