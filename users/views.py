from rest_framework import (
    permissions,
    response,
    status,
    views,
    viewsets,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from utils import helper
from .models import *
from .serializers import *
from .app_utils import EmailPhoneUsernameAuthentication as EPUA
from .app_utils import get_tokens_for_user

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings


# from core import settings

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @staticmethod
    def _otp_login(request, serializer):
        resp = response.Response()

        # setting the jwt cookies
        # set_jwt_cookies(
        #     response=resp,
        #     access_token=serializer.validated_data.get(
        #         settings.JWT_AUTH_COOKIE
        #     ),
        #     refresh_token=serializer.validated_data.get(
        #         settings.JWT_AUTH_REFRESH_COOKIE
        #     ),
        # )

        resp.set_cookie('access',
                        str(serializer.validated_data.get(settings.JWT_AUTH_COOKIE)),
                        httponly=True)
        resp.set_cookie('refresh',
                        str(serializer.validated_data.get(settings.JWT_AUTH_REFRESH_COOKIE)),
                        httponly=True)

        resp.status_code = status.HTTP_200_OK
        resp.data = {
            "detail": "Login successfully",
            "data": serializer.validated_data,
        }
        return resp

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        resp = response.Response()
        try:
            # user = EPUA.authenticate(
            #     request=request,
            #     username=request.data.get("phone_number"),
            #     otp=request.data.get("otp"),
            # )
            try:
                return self._otp_login(
                    request=request,
                    serializer=serializer
                )

            except Exception as e:
                # raise InvalidToken(e.args[0]) from e
                return response.Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)

        except Exception:

            resp.data = {
                "message": "Username or Password error",
                "data": serializer.validated_data,
            }
            return response.Response(resp, status=status.HTTP_200_OK)


class GetNumberViewSet(viewsets.ModelViewSet):
    serializer_class = NumberObtainPairSerializer
    queryset = User.objects.all()
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        # serializer = self.serializer_class(data=request.data)
        data = request.data
        if "phone" in data:
            phone = data["phone"]
            get_user = self.queryset.filter(phone_number=phone)
            if not get_user:
                return response.Response(
                    "No User Found",
                    status=status.HTTP_404_NOT_FOUND
                )

            expires = datetime.now() + timedelta(seconds=310)
            base_otp = pyotp.TOTP('base32secret3232').now()
            user = get_user.first()
            OTPModel.objects.create(
                user=user,
                key=base_otp,
                expires_at=expires
            )
            send_mail(
                "Vangti OTP",
                f"Dear Customer,\nYour One-Time-Password for Vangti app is {base_otp}\nRegards,\nVangti Team",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return response.Response(
                "OTP sent in mail/sms",
                status=status.HTTP_200_OK
            )

        # serializer.is_valid(raise_exception=True)
        return response.Response(
            "please Input proper data",
            status=status.HTTP_200_OK
        )
