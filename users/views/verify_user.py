from rest_framework import (
    permissions,
    response,
    status,
    views,
    viewsets,
)
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework_simplejwt.views import TokenObtainPairView
from ..models import *
from ..serializers import *
from ..app_utils import get_reg_token
from django.conf import settings


class UserInformationViewSet(viewsets.ModelViewSet):
    queryset = UserInformation.objects.all()
    serializer_class = UserInformationRetrieveSerializer
    permission_classes = [permissions.IsAuthenticated]

    # http_method_names = ["get"]

    def user_info(self, *args, **kwargs):
        user = self.request.user
        instance = self.queryset.filter(user=user).first()
        serializer = self.serializer_class(instance, context={''})
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def change_profile(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(
            instance=user.user_info,
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user == -1:
            return response.Response({
                "message": "Invalid User",
                "data": serializer.validated_data,
            },
                status=status.HTTP_400_BAD_REQUEST
            )
        return response.Response(
            "Profile changed Successfully",
            status=status.HTTP_200_OK
        )


class UserNidInformationViewSet(viewsets.ModelViewSet):
    queryset = UserNidInformation.objects.all()
    serializer_class = AddNidSerializer
    permission_classes = [permissions.IsAuthenticated]
    # renderer_classes = [MultiPartParser,TemplateHTMLRenderer]
    # parser_classes = [FileUploadParser]

    def get_serializer_class(self):
        if self.action in ["update_nid", "retrieve"]:
            return UpdateNidSerializer
        if self.action == "nid_front_add":
            return FrontNidSerializer
        if self.action == "nid_back_add":
            return BackNidSerializer
        if self.action == "nid_photo_add":
            return PhotoNidSerializer
        if self.action == "nid_signature_add":
            return SignNidSerializer
        return self.serializer_class

    def retrieve(self, request, *args, **kwargs):
        instance = self.queryset.get(user=self.request.user)
        serializer = self.get_serializer_class()(instance)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def add_nid(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(
            data=request.data,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            # after validating photo and signature, send to response
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response("not valid data", status=status.HTTP_400_BAD_REQUEST)

    def nid_front_add(self, request, *args, **kwargs):
        instance = self.queryset.get(user=self.request.user)
        # self.parser_classes = MultiPartParser
        serializer = self.get_serializer_class()(
            instance,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            # after validating photo and signature, send to response
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response("not valid data", status=status.HTTP_400_BAD_REQUEST)

    def nid_back_add(self, request, *args, **kwargs):
        instance = self.queryset.get(user=self.request.user)
        serializer = self.get_serializer_class()(
            instance,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            # after validating photo and signature, send to response
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response("not valid data", status=status.HTTP_400_BAD_REQUEST)

    def nid_photo_add(self, request, *args, **kwargs):
        instance = self.queryset.get(user=self.request.user)
        serializer = self.get_serializer_class()(
            instance,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            # after validating photo and signature, send to response
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response("not valid data", status=status.HTTP_400_BAD_REQUEST)

    def nid_signature_add(self, request, *args, **kwargs):
        instance = self.queryset.get(user=self.request.user)
        serializer = self.get_serializer_class()(
            instance,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            # after validating photo and signature, send to response
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response("not valid data", status=status.HTTP_400_BAD_REQUEST)

    def update_nid(self, request, *args, **kwargs):
        instance = self.queryset.get(user=self.request.user)
        serializer = self.get_serializer_class()(
            instance,
            data=request.data,
            context={'request': request},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            # after validating photo and signature, send to response
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response("not valid data", status=status.HTTP_400_BAD_REQUEST)

    # send to porichoy/something
    def validate_information(self, *args, **kwargs):
        return


class UserKYCDocumentViewSet(viewsets.ModelViewSet):
    queryset = UserKYCDocument.objects.all()
    serializer_class = UserKYCDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserKYCInformationViewSet(viewsets.ModelViewSet):
    queryset = UserKYCInformation.objects.all()
    serializer_class = AddKycSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'update_kyc_information':
            return UpdateKycSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def add_kyc_info(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response("not valid data", status=status.HTTP_400_BAD_REQUEST)

    def update_kyc_information(self, request, *args, **kwargs):
        instance = self.queryset.get(user=request.user)
        print(instance)
        serializer = self.get_serializer_class()(
            instance, data=self.request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        return response.Response("not valid data", status=status.HTTP_400_BAD_REQUEST)


class VerifiedUsersViewSet(viewsets.ModelViewSet):
    queryset = VerifiedUsers.objects.all()
    serializer_class = VerifiedUsersSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data, context={"request": self.request})
        if serializer.is_valid():
            v_user = serializer.save()
            if v_user != -1:
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        return response.Response("data not valid", status=status.HTTP_400_BAD_REQUEST)
