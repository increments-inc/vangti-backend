from typing import Any, Dict, Optional, Type, TypeVar
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import AbstractBaseUser, update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken, SlidingToken, Token, UntypedToken
from .app_utils import EmailPhoneUsernameAuthentication as EPUA


AuthUser = TypeVar("AuthUser", AbstractBaseUser, TokenUser)


class TokenObtainSerializer(serializers.Serializer):
    username_field = get_user_model().USERNAME_FIELD
    token_class: Optional[Type[Token]] = None

    default_error_messages = {
        "no_active_account": _("No active account found with the given credentials")
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField(write_only=True)
        self.fields["pin"] = serializers.CharField(write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[Any, Any]:
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "pin": attrs["pin"]
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass
        
        self.user = EPUA.authenticate(
            request=self.context.get("request"),
            username=authenticate_kwargs["phone_number"],
            pin=authenticate_kwargs["pin"],
        )
        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.PermissionDenied(
                self.error_messages["no_active_account"],
                "no_active_account",
            )
        return {}

    @classmethod
    def get_token(cls, user: AuthUser) -> Token:
        return cls.token_class.for_user(user)  # type: ignore


class TokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data
