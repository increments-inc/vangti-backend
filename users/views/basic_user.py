from rest_framework import (
    permissions,
    response,
    status,
    views,
    viewsets,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from ..models import *
from ..serializers import *
from ..app_utils import get_reg_token
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import logout
from ..auth_jwt import JWTAccessToken


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = []
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
            "detail": "Login successful",
            "data": serializer.validated_data,
        }
        return resp

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=CustomTokenObtainPairSerializer,
                examples=[
                    OpenApiExample(
                        "login successful",
                        value={
                            "detail": "Login successful",
                            "data": {
                                "refresh": "string",
                                "access": "string"
                            }
                        }
                    )
                ],
            ),
            400: OpenApiResponse(
                response=CustomTokenObtainPairSerializer,
                examples=[
                    OpenApiExample(
                        "login error",
                        value={
                            "detail": "No active account found with the given credentials"
                        }
                    )
                ],
            )
        }
    )
    def post(self, request, *args, **kwargs):
        print(request.data)
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
            return response.Response(resp, status=status.HTTP_400_BAD_REQUEST)


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = []

    def get_serializer_class(self):
        if self.action == "set_pin":
            return UserPINSerializer
        if self.action == "reset_pin":
            return UserPINResetSerializer
        return self.serializer_class

    @staticmethod
    def _otp_reg(request, user, serializer):
        resp = response.Response()
        reg_token = str(get_reg_token(user))
        resp.set_cookie('reg_token',
                        reg_token,
                        httponly=True)

        resp.status_code = status.HTTP_200_OK
        resp.data = {
            "detail": "Registration successful",
            # "reg_access_token": reg_token,
        }
        return resp

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user == -1:
            return response.Response({
                "message": "OTP doesnt match",
                "data": serializer.validated_data,
            },
                status=status.HTTP_404_NOT_FOUND
            )
        resp = response.Response()
        try:
            try:
                return self._otp_reg(
                    request=request,
                    user=user,
                    serializer=serializer
                )

            except Exception as e:
                # raise InvalidToken(e.args[0]) from e
                return response.Response(e.args[0], status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            resp.data = {
                "message": "Registration Error",
                "data": serializer.validated_data,
            }
            return response.Response(resp, status=status.HTTP_404_NOT_FOUND)

    def set_pin(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user == -1:
            return response.Response({
                "message": "Invalid PIN or invalid device",
                "data": serializer.validated_data,
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        return response.Response(
            "PIN Set Successfully",
            status=status.HTTP_200_OK
        )

    def reset_pin(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user == -1:
            return response.Response({
                "message": "user does not exist",
                "data": serializer.validated_data,
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        return response.Response(
            "PIN Set Successfully",
            status=status.HTTP_200_OK
        )


class UserPinViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = PINSerializer
    permission_classes = [permissions.IsAuthenticated]

    def set_pin(self, request, *args, **kwargs):
        token = request.headers.get('Authorization').split()[1]  # Extract token
        token.blacklist()  # Blacklist after use
        user = request.user
        serializer = self.serializer_class(
            instance=user,
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user == -1:
            return response.Response({
                "message": "Invalid PIN or invalid device",
                "data": serializer.validated_data,
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        return response.Response(
            "PIN Set Successfully",
            status=status.HTTP_200_OK
        )


class GetNumberViewSet(viewsets.ModelViewSet):
    permission_classes = []
    serializer_class = RegistrationOTPSerializer
    queryset = RegistrationOTPModel.objects.all()
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        # serializer = self.serializer_class(data=request.data)
        data = request.data
        print(data)
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            user = serializer.save()
            if user == -1:
                return response.Response(
                    "User exists!",
                    status=status.HTTP_302_FOUND
                )
            return response.Response(
                "OTP sent in mail/sms",
                status=status.HTTP_200_OK
            )

        # serializer.is_valid(raise_exception=True)
        return response.Response(

            "Input proper data",
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserDeactivateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "deactivate_user":
            return UserDeactivateSerializer
        if self.action == "change_pin":
            return PINSerializer
        # if self.action == "phone_register":
        #     return PhoneRegisterSerializer
        return self.serializer_class

    def perform_update(self, serializer):
        serializer.save()

    def deactivate_user(self, request, *args, **kwargs):
        instance = request.user
        data = request.data
        serializer = self.get_serializer_class()(instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                "User Deactivated",
                status=status.HTTP_200_OK
            )
        return response.Response(
            "",
            status=status.HTTP_200_OK
        )

    def delete_user(self, request, *args, **kwargs):
        # cretae db and run crontab
        return response.Response(
            "",
            status=status.HTTP_200_OK
        )

    def change_pin(self, request, *args, **kwargs):
        # Blacklist after use
        user = request.user
        serializer = self.get_serializer_class()(
            instance=user,
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user == -1:
            return response.Response({
                "message": "Invalid PIN or invalid device",
                "data": serializer.validated_data,
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        return response.Response(
            "PIN Set Successfully",
            status=status.HTTP_200_OK
        )


class PhoneUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = PhoneRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def phone_register(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        return response.Response(
            "",
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args):
        refresh_token = request.data["refresh"]
        token = request.META.get("HTTP_AUTHORIZATION", "").replace("Bearer ", "")
        try:
            refresh_token_blacklist = RefreshToken(refresh_token).blacklist()
            access_token_blacklist = JWTAccessToken(token).blacklist()
            return response.Response("Logout successful", status=status.HTTP_200_OK)
        except:
            return response.Response("Logout not successful, check refresh token", status=status.HTTP_400_BAD_REQUEST)


