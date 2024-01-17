import uuid
import pyotp
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Permission
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, FileExtensionValidator
from core.abstract_models import models, BaseModel
from django.contrib.auth.models import BaseUserManager
from utils.helper import content_file_path, ImageCompress

STATUS_OPTION = (
    ('PENDING', 'Pending'),
    ('ACTIVE', 'Active'),
    ('INACTIVE', 'Inactive'),
)


class UserManager(BaseUserManager):
    """
    This is the manager for custom user model
    """

    def create_user(self, email, phone_number, pin=None, password=None):
        if not phone_number:
            raise ValueError("phone_number should not be empty")

        # if not password:
        #     raise ValueError("Password should not be empty")
        if email:
            user = self.model(
                phone_number=phone_number,
                email=self.normalize_email(email=email),
                pin=pin
            )
        else:
            user = self.model(
                phone_number=phone_number,
                pin=pin
            )
        # if password:
        #     user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email=None, password=None):
        user = self.create_user(
            email=email,
            phone_number=phone_number,
            password=password,
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model Class
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        verbose_name="ID",
    )
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+880XXXX-XXXXXX'. Up to 13 "
                                         "digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=15, unique=True)
    email = models.EmailField(null=True, blank=True)

    pin = models.CharField(max_length=750, null=True)

    # status = models.CharField(choices=STATUS_OPTION, default='PENDING', max_length=15)
    # is_provider = models.BooleanField(default=False)

    date_joined = models.DateTimeField(
        verbose_name="Date Joined",
        auto_now_add=True,
    )
    last_login = models.DateTimeField(
        auto_now=True,
    )

    is_staff = models.BooleanField(
        verbose_name="Staff Status",
        default=False,
        help_text="Designate if the user has " "staff status",
    )
    is_active = models.BooleanField(
        verbose_name="Active Status",
        default=True,
        help_text="Designate if the user has " "active status",
    )
    is_superuser = models.BooleanField(
        verbose_name="Superuser Status",
        default=False,
        help_text="Designate if the " "user has superuser " "status",
    )

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = [
        # "email",
    ]

    objects = UserManager()

    def __str__(self):
        return self.phone_number


# class OTPModel(models.Model):
#     """
#     Model to handle user OTP
#     """
#
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="user_otp",
#     )
#     key = models.TextField(
#         unique=True,
#         blank=True,
#         null=True,
#     )
#     is_active = models.BooleanField(
#         default=False,
#     )
#     expires_at = models.DateTimeField(null=True)
#
#     def __str__(self):
#         return f"OTP - {self.user.phone_number}"


class RegistrationOTPModel(BaseModel):
    """
    Model to handle user OTP during registration
    """
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+880XXXX-XXXXXX'. Up to 13 "
                                         "digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=15)
    device_token = models.CharField(max_length=512, null=True, blank=True)
    key = models.TextField(
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(
        default=False,
    )
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"OTP - {self.phone_number}"
