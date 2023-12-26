import contextlib, json, random, pyotp, re
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models import Q
from django.urls import exceptions as url_exceptions
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers, validators
from rest_framework_simplejwt import settings as jwt_settings
from rest_framework_simplejwt import tokens
from rest_framework_simplejwt.exceptions import TokenError
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .app_rest import TokenObtainPairSerializer
from . import models
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from .pin_validator import PINValidator
from django.contrib.auth.hashers import PBKDF2PasswordHasher


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["email"] = user.email
        token["is_superuser"] = user.is_superuser
        token["is_staff"] = user.is_staff
        return token

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # self.fields['phone_number'] = serializers.CharField()
    #     self.fields['otp'] = serializers.IntegerField()
    #     self.fields.pop("password")
    #
    # def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
    #     authenticate_kwargs = {
    #         self.username_field: attrs[self.username_field],
    #
    #     }
    #     try:
    #         authenticate_kwargs["request"] = self.context["request"]
    #     except KeyError:
    #         pass
    #
    #     self.user = login(**authenticate_kwargs)
    #     #
    #     # if not api_settings.USER_AUTHENTICATION_RULE(self.user):
    #     #     raise exceptions.AuthenticationFailed(
    #     #         self.error_messages["no_active_account"],
    #     #         "no_active_account",
    #     #     )
    #
    #     return {}


# use login
class NumberObtainPairSerializer(serializers.Serializer):
    phone = serializers.CharField()

    # class Meta:
    #     model = models.User
    #     fields = ("phone_number",)



class RegistrationOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RegistrationOTPModel
        fields = ("phone_number",)

    def create(self, validated_data):
        print("here")
        phone_number = validated_data.pop("phone_number", None)
        if models.User.objects.filter(
            phone_number=phone_number
        ).exists():
            return -1
        time_now = datetime.now()
        expires = time_now + timedelta(seconds=310)
        base_otp = pyotp.TOTP('base32secret3232').now()

        reg_phone = models.RegistrationOTPModel.objects.create(
            phone_number=phone_number,
            key=base_otp,
            expires_at=expires
        )
        host_user = settings.EMAIL_HOST_USER
        # insert sms service here
        send_mail(
            "Vangti OTP",
            f"Dear Customer,\nYour One-Time-Password for Vangti app is {base_otp}\nRegards,\nVangti Team",
            host_user,
            [host_user],
            fail_silently=False,
        )
        return reg_phone


class RegistrationSerializer(serializers.ModelSerializer):
    otp = serializers.CharField(allow_null=True)

    class Meta:
        model = models.User
        fields = ("phone_number", "otp",)

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number", None)
        otp = validated_data.pop("otp", None)
        time_now = datetime.now()
        try:
            reg = models.RegistrationOTPModel.objects.get(
                phone_number=phone_number,
                expires_at__gte=time_now
            )
            if str(reg.key) != otp:
                return -1
            user = models.User.objects.create(
                phone_number=phone_number,
                pin=None
            )
        except models.RegistrationOTPModel.DoesNotExist:
            return -1
        return user


class PINSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ("pin",)

    def update(self, instance, validated_data):
        pin = validated_data.pop("pin", None)
        # try:
        PINValidator().validate(password=pin)
        hasher = PBKDF2PasswordHasher()
        hashed_pin = hasher.encode(pin, settings.SALT)
        instance.pin = hashed_pin
        instance.save()
        # except:
        #     return -1
        return instance



class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.IntegerField()



class Login0(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"})

    def authenticate(self, **kwargs):
        return authenticate(self.context["request"], **kwargs)

    def _validate_email(self, email, password):
        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _(
                'Must include either "username" or "email" and "password".',
            )
            raise exceptions.ValidationError(msg)

        return user

    def get_auth_user_using_allauth(self, username, email, password):
        from allauth.account import app_settings

        # Authentication through email
        if (
                app_settings.AUTHENTICATION_METHOD
                == app_settings.AuthenticationMethod.EMAIL
        ):
            return self._validate_email(email, password)

        # Authentication through username
        if (
                app_settings.AUTHENTICATION_METHOD
                == app_settings.AuthenticationMethod.USERNAME
        ):
            return self._validate_username(username, password)

        # Authentication through either username or email
        return self._validate_username_email(username, email, password)

    def get_auth_user_using_orm(self, username, email, password):
        if email:
            with contextlib.suppress(models.User.DoesNotExist):
                username = models.User.objects.get(
                    email__iexact=email,
                ).get_username()
        if username:
            return self._validate_username_email(username, "", password)

        return None

    def get_auth_user(self, username, email, password):
        """
        Retrieve the auth user from given POST payload by using
        either `allauth` auth scheme or bare Django auth scheme.

        Returns the authenticated user instance if credentials are correct,
        else `None` will be returned
        """
        if "allauth" in settings.INSTALLED_APPS:
            # When `is_active` of a user is set to False,
            # allauth tries to return template html
            # which does not exist. This is the solution for it.
            # See issue #264.
            try:
                return self.get_auth_user_using_allauth(
                    username,
                    email,
                    password,
                )
            except url_exceptions.NoReverseMatch as e:
                msg = _("Unable to log in with provided credentials.")
                raise exceptions.ValidationError(msg) from e
        return self.get_auth_user_using_orm(username, email, password)

    @staticmethod
    def validate_auth_user_status(user):
        if not user.is_active:
            msg = _("User account is disabled.")
            raise exceptions.ValidationError(msg)

    @staticmethod
    def validate_email_verification_status(user):
        from allauth.account import app_settings

        if (
                app_settings.EMAIL_VERIFICATION
                == app_settings.EmailVerificationMethod.MANDATORY
                and not user.emailaddress_set.filter(
            email=user.email, verified=True
        ).exists()
        ):
            raise serializers.ValidationError(_("E-mail is not verified."))

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")
        user = self.get_auth_user(username, email, password)

        if not user:
            msg = _("Unable to log in with provided credentials.")
            raise exceptions.ValidationError(msg)

        # Did we get back an active user?
        self.validate_auth_user_status(user)

        # If required, is the email verified?
        if "dj_rest_auth.registration" in settings.INSTALLED_APPS:
            self.validate_email_verification_status(user)

        attrs["user"] = user
        return attrs

    class Meta:
        pass


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    token_class = tokens.RefreshToken

    def validate(self, attrs):
        try:
            refresh = self.token_class(attrs["refresh"])
        except TokenError as e:
            raise exceptions.AuthenticationFailed(detail=e) from e

        data = {"access": str(refresh.access_token)}

        if jwt_settings.api_settings.ROTATE_REFRESH_TOKENS:
            if jwt_settings.api_settings.BLACKLIST_AFTER_ROTATION:
                with contextlib.suppress(AttributeError):
                    # Attempt to blacklist the given refresh token
                    # If blacklist app not installed, `blacklist` method
                    # will not be present
                    refresh.blacklist()
            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh"] = str(refresh)

        return data

    class Meta:
        pass


class NewUserSerializer(serializers.ModelSerializer):
    """
    New User Registration Serializer
    """

    email = serializers.EmailField(
        required=True,
        validators=[
            validators.UniqueValidator(
                queryset=models.User.objects.all(),
            )
        ],
    )
    username = serializers.CharField(
        required=True, validators=[UnicodeUsernameValidator()]
    )

    phone_number = serializers.CharField(
        required=True
    )

    password1 = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
        label="Retype Password",
    )

    # others information
    company_name = serializers.CharField(
        required=True, write_only=True
    )
    address = serializers.CharField(
        required=True, write_only=True
    )
    location = serializers.CharField(
        required=True, write_only=True
    )
    person_name = serializers.CharField(
        required=True, write_only=True
    )
    profile_pic = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True, write_only=True)

    class Meta:
        model = models.User
        fields = ["username", "email", "phone_number", "password1", "password2", "person_name", "location", "address",
                  "company_name", "profile_pic",
                  ]

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise validators.ValidationError(
                {
                    "password1": "Password Doesn't Match",
                }
            )
        if models.User.objects.filter(Q(username=attrs["username"]) | Q(phone_number=attrs['phone_number'])).exists():
            raise validators.ValidationError(
                {"username": "user with this Username or phone number already exists."}
            )
        return attrs

    def create(self, validated_data):
        user = models.User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            phone_number=validated_data["phone_number"],
        )
        user.set_password(validated_data["password1"])
        user.save()

        user_info = models.UserInformationModel.objects.get(user=user)

        user_info.person_name = validated_data["person_name"]
        user_info.company_name = validated_data["company_name"]
        user_info.address = validated_data["address"]
        user_info.location = validated_data["location"]
        user_info.profile_pic = validated_data["profile_pic"]
        user_info.save()
        return user


class UserInformationSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = models.UserInformation
        fields = "__all__"

    def get_profile_pic(self, obj):
        request = self.context.get("request")
        photo_url = obj.profile_pic.url
        return request.build_absolute_uri(photo_url)


class UserSerializer(serializers.ModelSerializer):
    """
    New User Registration Serializer for students
    """

    user_information = UserInformationSerializer(read_only=True)
    email = serializers.EmailField(
        required=False,
        validators=[
            validators.UniqueValidator(
                queryset=models.User.objects.all(),
            )
        ],
        write_only=True,
        allow_blank=True,
        allow_null=True,
    )
    # username = serializers.CharField(
    #     required=True, validators=[UnicodeUsernameValidator()]
    # )

    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
        validators=[validate_password],
    )

    # user information fields
    profile_pic = serializers.ImageField(required=False, write_only=True)
    first_name = serializers.CharField(required=False, write_only=True)
    last_name = serializers.CharField(required=False, write_only=True)
    # male female other choices
    gender = serializers.ChoiceField(
        required=False, choices=["MALE", "FEMALE", "OTHER"], write_only=True
    )

    class Meta:
        model = models.User
        fields = [
            "email",
            "password",
            "profile_pic",
            "first_name",
            "last_name",
            "gender",
            "user_information",
        ]

    # def validate(self, attrs):
    #     if models.User.objects.filter(username=attrs["email"]).exists():
    #         raise validators.ValidationError(
    #             {"username": "user with this User ID already exists."}
    #         )
    #     return attrs

    def create(self, validated_data):
        if validated_data["email"] == "":
            email = self.__create_email(
                validated_data["first_name"], validated_data["last_name"]
            )
        else:
            email = validated_data["email"]
        username = self._create_username(email)
        user = models.User.objects.create(email=email, username=username)
        user.set_password(validated_data["password"])
        user.save()

        user.user_information.profile_pic = validated_data["profile_pic"]
        user.user_information.first_name = validated_data["first_name"]
        user.user_information.last_name = validated_data["last_name"]
        user.user_information.gender = validated_data["gender"]
        # user.user_information.phone_number = self.context["phone_number"]
        user.user_information.is_student = True
        user.user_information.save()
        return user

    def _create_username(self, email):
        """
        Create a unique username for the user.
        """
        username = email
        if username is None:
            return None
        username = username.split("@")[0]
        username = username.replace(".", "")
        username = username.replace("_", "")
        username = username.replace("-", "")
        username = username.lower()
        if username == "":
            return None
        if models.User.objects.filter(username=username).exists():
            username = username + str(random.randint(1, 1000))
        return username

    def __create_email(self, first_name, last_name):
        email = first_name + last_name + "@gmail.com"
        email = email.lower().strip()
        num = 1
        while models.User.objects.filter(email=email).exists():
            email = first_name + last_name + str(num) + "@gmail.com"
            num += 1
        return email

    def get_profile_pic(self, obj):
        request = self.context.get("request")
        photo_url = obj.profile_pic.url
        return request.build_absolute_uri(photo_url)


class PasswordValidateSerializer(serializers.Serializer):
    """
    Serializer for validating password
    """

    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    old_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )
    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )
    retype_password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True,
        required=True,
    )


# ============***********============
# Password reset serializer
# ============***********============
class EmailSerializer(serializers.Serializer):
    """
    Reset Password Email Request Serializer.
    """

    email = serializers.EmailField(required=True)

    class Meta:
        fields = ("email",)


# ============***********============
# OTP BASED SERIALIZER PASSWORD RESET
# ============***********============
class PasswordResetVerifySerializer(serializers.Serializer):
    one_time_password = serializers.CharField()

    def validate_one_time_password(self, value):
        token = self.context.get("token")
        user, otp, _decrypted_data = self._validate_user(token)
        if otp != value:
            raise serializers.ValidationError("OTP Invalid")
        hotp = pyotp.HOTP(user.user_otp.key)
        if not hotp.verify(value, 1):
            raise serializers.ValidationError("Invalid one-time password")
        return self._verify_otp(_decrypted_data)

    def _validate_user(self, token):
        """
        Verify token and encoded_pk and then set new password.
        """
        # print()

        _decrypted_data = helper.decode(token)
        _decrypted_data_dict = json.loads(_decrypted_data.replace("'", '"'))

        # print(_decrypted_data)
        token = _decrypted_data_dict["token"]
        encoded_pk = _decrypted_data_dict["enc_pk"]
        otp = _decrypted_data_dict["otp"]

        if token is None or encoded_pk is None:
            raise serializers.ValidationError("Missing data.")

        pk = urlsafe_base64_decode(encoded_pk).decode()
        user = models.User.objects.get(pk=pk)
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("The reset token is invalid")
        return user, otp, _decrypted_data_dict

    def _verify_otp(self, _decrypted_data):
        _decrypted_data["verified"] = "True"
        _decrypted_data["verify_secret"] = settings.OTP_VERIFY_SECRET
        return helper.encode(str(_decrypted_data))

    def to_representation(self, instance):
        response = super(PasswordResetVerifySerializer, self).to_representation(
            instance
        )
        token = response.pop("one_time_password").split("'")[1]
        response["token"] = token
        return response


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    new_password_confirm = serializers.CharField()

    def validate(self, data):
        token = self.context.get("token")
        user = self._validate_user(token)
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError("Passwords do not match.")
        user.set_password(data["new_password"])
        user.save()
        return data

    def _validate_user(self, token):
        """
        Verify token and encoded_pk and then set new password.
        """
        # print()

        _decrypted_data = helper.decode(token)
        _decrypted_data_dict = json.loads(_decrypted_data.replace("'", '"'))
        # print(_decrypted_data)
        token = _decrypted_data_dict["token"]
        encoded_pk = _decrypted_data_dict["enc_pk"]
        verified = _decrypted_data_dict["verified"]
        verify_secret = _decrypted_data_dict["verify_secret"]
        if self._validate_otp_verified(verified, verify_secret):
            if token is None or encoded_pk is None:
                raise serializers.ValidationError("Missing data.")

            pk = urlsafe_base64_decode(encoded_pk).decode()
            user = models.User.objects.get(pk=pk)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("The reset token is invalid")
            return user
        raise serializers.ValidationError("OTP not verified")

    def _validate_otp_verified(self, verified, verify_secret):
        return bool(verified and verify_secret == settings.OTP_VERIFY_SECRET)
