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
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from ..auth_jwt import JWTAccessToken
from utils.log import logger


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = []
    serializer_class = CustomTokenObtainPairSerializer

    @staticmethod
    def _otp_login(request, serializer):
        resp = response.Response()
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
                            "refresh": "string",
                            "access": "string"
                        }
                    )
                ],
            ),
        }
    )
    def post(self, request, *args, **kwargs):
        logger.info(request.data)
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        # serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            return self._otp_login(
                request=request,
                serializer=serializer
            )
        return response.Response({
            "message": "Username or Password error",
            "errors": "invalid username or password",
        }, status=status.HTTP_400_BAD_REQUEST)


class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = []

    def get_serializer_class(self):
        # if self.action == "set_pin":
        #     return UserPINSerializer
        # if self.action == "reset_pin":
        #     return UserPINResetSerializer
        return self.serializer_class

    def post(self, request, *args, **kwargs):
        logger.info("data", request.data)
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            user = serializer.save()
            if user == -1:
                return response.Response({
                    "message": "Phone numer is not verified",
                    "data": serializer.validated_data,
                }, status=status.HTTP_400_BAD_REQUEST)
            if user == -2:
                return response.Response({
                    "message": "OTP doesnt match",
                    "data": serializer.validated_data,
                }, status=status.HTTP_404_NOT_FOUND)

            return response.Response({
                "detail": "Successful",
                # "reg_access_token": reg_token,
            }, status=status.HTTP_200_OK)

        return response.Response({
            "message": "Registration Error",
            # "reg_access_token": reg_token,
        }, status=status.HTTP_400_BAD_REQUEST)

    # def set_pin(self, request, *args, **kwargs):
    #     serializer = self.get_serializer_class()(
    #         data=request.data,
    #         context={"request": request}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.save()
    #     if user == -1:
    #         return response.Response({
    #             "message": "Invalid PIN or invalid device",
    #             # "data": serializer.validated_data,
    #         },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     if user == -2:
    #         return response.Response({
    #             "message": "PIN already set!",
    #             # "data": serializer.validated_data,
    #         },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     return response.Response(
    #         "PIN Set Successfully",
    #         status=status.HTTP_200_OK
    #     )

    # def reset_pin(self, request, *args, **kwargs):
    #     serializer = self.get_serializer_class()(
    #         data=request.data,
    #         context={"request": request}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.save()
    #     if user == -1:
    #         return response.Response({
    #             "message": "user does not exist",
    #             "data": serializer.validated_data,
    #         },
    #             status=status.HTTP_400_BAD_REQUEST
    #         )
    #     return response.Response(
    #         "PIN Set Successfully",
    #         status=status.HTTP_200_OK
    #     )


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
    http_method_names = ["post", "patch"]

    def get_serializer_class(self):
        if self.action == "verify_otp":
            return RegistrationOTPVerifySerializer
        return self.serializer_class

    def post(self, request, *args, **kwargs):
        logger.info("data", request.data)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user == -1:
                return response.Response(
                    {"errors": "User exists!"},
                    status=status.HTTP_302_FOUND
                )
            if user == -2:
                return response.Response(
                    {"errors": "User does not exist!"},
                    status=status.HTTP_404_NOT_FOUND
                )
            return response.Response(
                f"OTP sent via sms",
                status=status.HTTP_200_OK
            )
        return response.Response(
            {"details": "Input proper data"},
            status=status.HTTP_400_BAD_REQUEST
        )

    def verify_otp(self, *args, **kwargs):
        logger.info( "req data",self.request.data)
        phone_number = self.request.data.get("phone_number")
        if phone_number is not None:
            instance = self.queryset.filter(
                phone_number=phone_number
            )
            if instance.exists():
                if instance.filter(is_active=True).exists():
                    return response.Response(
                        "Phone number already verified",
                        status=status.HTTP_200_OK
                    )
                if not instance.filter(expires_at__gte=datetime.now()).exists():
                    return response.Response(
                        {"details": "OTP Expired"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                instance = instance.last()
                serializer = self.get_serializer_class()(instance, data=self.request.data)
                if serializer.is_valid():
                    data = serializer.save()
                    if data == -1:
                        return response.Response(
                            {"errors": "Incorrect OTP, phone number could not be verified"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    return response.Response(
                        "Phone number verified",
                        status=status.HTTP_200_OK
                    )
            return response.Response(
                {"details": "Phone number invalid"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return response.Response(
            {"details": "Input proper data"},
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
        if self.action == "delete_user":
            return UsersDeletionScheduleSerializer
        return self.serializer_class

    def perform_update(self, serializer):
        serializer.save()

    def deactivate_user(self, request, *args, **kwargs):
        instance = request.user
        data = request.data
        serializer = self.get_serializer_class()(
            instance, data=data, context={'request': request}
        )
        if serializer.is_valid():
            user = serializer.save()
            if user == -1:
                return response.Response(
                    {"message": "PIN is not valid"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == -2:
                return response.Response(
                    {"message": "PIN could not be validated"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return response.Response(
                "User Deactivated",
                status=status.HTTP_200_OK
            )
        return response.Response(
            "",
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete_user(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.save()
            if user == -2:
                return response.Response({"errors": "pin not verified"}, status=status.HTTP_400_BAD_REQUEST)
            if user == -3:
                return response.Response({"errors": "pin could not be validated"}, status=status.HTTP_400_BAD_REQUEST)

            return response.Response("User to be deleted in 30 days", status=status.HTTP_200_OK)
        return response.Response(
            {"message": "User Deletion failed"},
            status=status.HTTP_400_BAD_REQUEST
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


class LogoutView(views.APIView):
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
            return response.Response(
                {"errors": "Logout not successful, check refresh token"},
                status=status.HTTP_400_BAD_REQUEST
            )
